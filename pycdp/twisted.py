import json
import itertools
import typing as t
from collections import defaultdict
from contextlib import asynccontextmanager
from twisted.internet import reactor
from twisted.internet.error import ConnectionRefusedError
from twisted.web.client import Agent, Response, readBody
from twisted.internet.defer import DeferredQueue, QueueOverflow, Deferred, CancelledError
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from pycdp.exceptions import *
from pycdp.base import IEventLoop
from pycdp.utils import ContextLoggerMixin, LoggerMixin, retry_on
from pycdp import cdp


T = t.TypeVar('T')


class TwistedEventLoop(IEventLoop):

    def __init__(self, reactor):
        self._reactor = reactor

    async def sleep(self, delay: float):
        sleep = Deferred()
        self._reactor.callLater(delay, sleep.callback, None)
        await sleep

loop = TwistedEventLoop(reactor)


_CLOSE_SENTINEL = object
class CDPEventListener:

    def __init__(self, queue: DeferredQueue):
        self._queue = queue
        self._closed = False

    @property
    def closed(self):
        return self._closed

    def put(self, elem: dict):
        if self._closed: raise CDPEventListenerClosed
        self._queue.put(elem)

    def close(self):
        self._closed = True
        try:
            self._queue.put(_CLOSE_SENTINEL)
        except QueueOverflow:
            pass

    async def __aiter__(self):
        try:
            while not self._closed:
                elem = await self._queue.get()
                if elem is _CLOSE_SENTINEL:
                    return
                yield elem
        finally:
            self._closed = True

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(buffer={len(self._queue.pending)}/{self._queue.size}, closed={self._closed})'


class CDPSocket(WebSocketClientProtocol):

    @property
    def closed(self) -> bool:
        return self.localCloseCode is not None or self.remoteCloseCode is not None

    def onConnect(self, response):
        self.factory.connection = self
        self.factory.connectWaiter.callback(None)

    def onCloseFrame(self, code, reasonRaw):
        return super().onCloseFrame(code, reasonRaw)

    async def close(self):
        self.dropConnection()
        await self.is_closed


class CDPConnector(WebSocketClientFactory):
    protocol = CDPSocket

    def startedConnecting(self, connector):
        self.connectWaiter = Deferred()

    def clientConnectionFailed(self, connector, reason):
        self.connectWaiter.errback(CDPError(f'CDP connection failed: {reason}'))


class CDPBase(LoggerMixin):

    def __init__(self, ws: CDPSocket=None, session_id=None, target_id=None):
        super().__init__()
        self._listeners: t.Dict[type, t.Set[CDPEventListener]] = defaultdict(set)
        self._id_iter = itertools.count()
        self._inflight_cmd: t.Dict[int, t.Tuple[t.Generator[dict, dict , t.Any], Deferred]] = {}
        self._session_id = session_id
        self._target_id = target_id
        self._ws: CDPSocket = ws

    @property
    def session_id(self) -> cdp.target.SessionID:
        return self._session_id

    async def execute(self, cmd: t.Generator[dict, dict , T]) -> T:
        '''
        Execute a command on the server and wait for the result.

        :param cmd: any CDP command
        :returns: a CDP result
        '''
        if self._ws.closedByMe:
            raise CDPConnectionClosed(f'{self._ws.localCloseReason} ({self._ws.localCloseCode})')
        if self._ws.remoteCloseCode is not None:
            raise CDPConnectionClosed(f'{self._ws.remoteCloseReason} ({self._ws.remoteCloseCode})')
        cmd_id = next(self._id_iter)
        cmd_response = Deferred()
        self._inflight_cmd[cmd_id] = cmd, cmd_response
        request = next(cmd)
        request['id'] = cmd_id
        if self._session_id:
            request['sessionId'] = self._session_id
        self._logger.debug('sending command %r', request)
        request_str = json.dumps(request)
        try:
            self._ws.sendMessage(request_str.encode('UTF-8'))
            return await cmd_response
        except CancelledError:
            if cmd_id in self._inflight_cmd:
                del self._inflight_cmd[cmd_id]
            raise

    def listen(self, *event_types: t.Type[T], buffer_size=100) -> t.AsyncIterator[T]:
        '''Return an async iterator that iterates over events matching the
        indicated types.'''
        receiver = CDPEventListener(DeferredQueue(buffer_size))
        for event_type in event_types:
            self._listeners[event_type].add(receiver)
        return receiver.__aiter__()

    @asynccontextmanager
    async def wait_for(self, event_type: t.Type[T], buffer_size=100) -> t.AsyncGenerator[T, None]:
        '''
        Wait for an event of the given type and return it.

        This is an async context manager, so you should open it inside an async
        with block. The block will not exit until the indicated event is
        received.
        '''
        async for event in self.listen(event_type, buffer_size):
            yield event
            return

    def close_listeners(self):
        for listener in itertools.chain.from_iterable(self._listeners.values()):
            listener.close()
        self._listeners.clear()

    def _handle_data(self, data):
        '''
        Handle incoming WebSocket data.

        :param dict data: a JSON dictionary
        '''
        if 'id' in data:
            self._handle_cmd_response(data)
        else:
            self._handle_event(data)

    def _handle_cmd_response(self, data):
        '''
        Handle a response to a command. This will set an event flag that will
        return control to the task that called the command.

        :param dict data: response as a JSON dictionary
        '''
        cmd_id = data['id']
        try:
            cmd, event = self._inflight_cmd.pop(cmd_id)
        except KeyError:
            self._logger.debug('got a message with a command ID that does not exist: %s', data)
            return
        if 'error' in data:
            # If the server reported an error, convert it to an exception and do
            # not process the response any further.
            event.errback(CDPBrowserError(data['error']))
        else:
            # Otherwise, continue the generator to parse the JSON result
            # into a CDP object.
            try:
                cmd.send(data['result'])
                event.errback(CDPInternalError("the command's generator function did not exit when expected!"))
            except StopIteration as e:
                event.callback(e.value)

    def _handle_event(self, data):
        '''
        Handle an event.

        :param dict data: event as a JSON dictionary
        '''
        event = cdp.util.parse_json_event(data)
        self._logger.debug('dispatching event %s', event)
        to_remove = set()
        for listener in self._listeners[type(event)]:
            try:
                listener.put(event)
            except QueueOverflow:
                self._logger.warning('event %s dropped because listener %s queue is full', type(event), listener)
            except CDPEventListenerClosed:
                to_remove.add(listener)
        self._listeners[type(event)] -= to_remove
        self._logger.debug('event dispatched')


class CDPConnection(CDPBase):

    def __init__(self, debugging_url: str, http_client: Agent, reactor):
        super().__init__()
        self._debugging_url = debugging_url.rstrip('/')
        self._http_client = http_client
        self._reactor = reactor
        self._wsurl: str = None
        self._sessions: t.Dict[str, CDPSession] = {}

    @property
    def closed(self) -> bool:
        return self._ws.closed

    @property
    def had_normal_closure(self) -> bool:
        return not self._ws.remoteCloseCode or (self._ws.closedByMe and self._ws.localCloseCode == 1000)

    @retry_on(ConnectionRefusedError, retries=10, delay=1.0, log_errors=True, loop=loop)
    async def connect(self):
        if self._ws is not None: raise RuntimeError('already connected')
        if self._wsurl is None:
            if self._debugging_url.startswith('http://'):
                version: Response = await self._http_client.request(
                    b'GET',
                    b'%s/json/version' % self._debugging_url.encode('UTF-8')
                )
                if version.code != 200:
                    raise CDPError(f'could not get {self._debugging_url}/json/version: HTTP {version.code} {version.phrase})')
                self._wsurl = json.loads(await readBody(version))['webSocketDebuggerUrl']
            elif self._debugging_url.startswith('ws://'):
                self._wsurl = self._debugging_url
            else:
                raise ValueError('bad debugging URL scheme')
        connector = CDPConnector(self._wsurl)
        self._reactor.connectTCP(connector.host, connector.port, connector)
        await connector.connectWaiter
        self._ws = connector.connection
        self._ws.onMessage = self._handleMessage

    def add_session(self, session_id: str, target_id: str) -> 'CDPSession':
        if session_id is self._sessions:
            return self._sessions[session_id]
        session = CDPSession(self._ws, session_id, target_id)
        self._sessions[session_id] = session
        return session

    def remove_session(self, session_id: str):
        if session_id in self._sessions:
            self._sessions.pop(session_id).close()

    async def connect_session(self, target_id: cdp.target.TargetID) -> 'CDPSession':
        '''
        Returns a new :class:`CDPSession` connected to the specified target.
        '''
        session_id = await self.execute(cdp.target.attach_to_target(target_id, True))
        session = CDPSession(self._ws, session_id, target_id)
        self._sessions[session_id] = session
        return session

    def _handleMessage(self, message: bytes, isBinary: bool):
        if isBinary: raise RuntimeError('unexpected binary ws message')
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            raise CDPBrowserError({
                'code': -32700,
                'message': 'Client received invalid JSON',
                'data': message
            })
        if 'sessionId' in data:
            session_id = cdp.target.SessionID(data['sessionId'])
            try:
                session = self._sessions[session_id]
            except KeyError:
                self._logger.debug(f'received message for unknown session: {data}')
            session._handle_data(data)
        else:
            self._handle_data(data)

    async def close(self):
        for session in self._sessions.values():
            session.close()
        self._sessions.clear()
        self.close_listeners()
        if self._ws is not None and not self._ws.closed:
            await self._ws.close()


class CDPSession(CDPBase, ContextLoggerMixin):
    def __init__(self, ws: CDPSocket, session_id: cdp.target.SessionID, target_id: cdp.target.TargetID):
        super().__init__(ws, session_id, target_id)
        self.set_logger_context(extra_name=session_id)

    def close(self):
        if len(self._inflight_cmd) > 0:
            exc = CDPSessionClosed()
            for (_, event) in self._inflight_cmd.values():
                if not event.called:
                    event.errback(exc)
            self._inflight_cmd.clear()
        self.close_listeners()


async def connect_cdp(url: str, reactor) -> CDPConnection:
    cdp_conn = CDPConnection(url, Agent(reactor), reactor)
    await cdp_conn.connect()
    return cdp_conn
