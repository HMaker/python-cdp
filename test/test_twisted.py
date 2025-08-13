import pytest

import pytest_twisted

from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.task import deferLater
from pycdp.twisted import CDPEventListener, CDPEventListenerClosed

from conftest import coroutine_might_block, timeoutDeferred


CDP_EVENT_LISTENER_Q_LIMIT = 10


class TestCDPEventListener:
    @pytest.fixture(scope="function", autouse=True)
    def create_cdp_event_listener(self):
        self.listener = CDPEventListener(CDP_EVENT_LISTENER_Q_LIMIT)

    @pytest_twisted.ensureDeferred
    async def test_simple_put(self):
        listener = self.listener
        listener.put({1: 1})
        listener.put({2: 2})

        iterator = aiter(listener)

        elems = []
        elems.append(await anext(iterator))
        elems.append(await anext(iterator))

        listener.put({3: 3})

        elems.append(await anext(iterator))

        expected = [{1: 1}, {2: 2}, {3: 3}]

        assert elems == expected

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_blocking_when_empty(self):
        listener = self.listener
        listener.put({1: 1})
        listener.put({2: 2})

        iterator = aiter(listener)

        elems = []
        elems.append(await anext(iterator))
        elems.append(await anext(iterator))

        task = anext(iterator)
        might_block, task = coroutine_might_block(task)
        assert might_block

        # Now, it shouldn't block anymore
        listener.put({3: 3})
        elems.append(await task)

        expected = [{1: 1}, {2: 2}, {3: 3}]

        assert elems == expected

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_queue_full(self):
        listener = self.listener
        iterator = aiter(listener)

        for i in range(CDP_EVENT_LISTENER_Q_LIMIT):
            listener.put({i: i})

        with pytest.raises(defer.QueueOverflow):
            listener.put({0: 0})

        await anext(iterator)
        await anext(iterator)

        listener.put({0: 0})
        listener.put({0: 0})

        with pytest.raises(defer.QueueOverflow):
            listener.put({0: 0})
            listener.put({0: 0})
            listener.put({0: 0})

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_queue_full_discard(self):
        """Tests that elements that don't fit the queue are actually discarded"""
        listener = self.listener
        iterator = aiter(listener)

        for i in range(CDP_EVENT_LISTENER_Q_LIMIT):
            listener.put({1: 1})

        with pytest.raises(defer.QueueOverflow):
            listener.put({0: 0})

        for i in range(CDP_EVENT_LISTENER_Q_LIMIT):
            assert await anext(iterator) == {1: 1}

        # Tests that the queue was emptied, so {0: 0} can't be there
        task = anext(iterator)
        assert coroutine_might_block(task)

        # Tests that {0: 0} is not somehow added later in the queue,
        #   when put is called
        listener.put({1: 1})
        assert await task == {1: 1}

        # Tests that the queue was emptied, so {0: 0} can't be there
        assert coroutine_might_block(anext(iterator))

    def test_close(self):
        listener = self.listener
        self.listener.close()

        assert self.listener.closed == True

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_put_after_close(self):
        listener = self.listener
        iterator = aiter(listener)

        listener.put({1: 1})
        listener.put({2: 2})
        listener.put({3: 3})

        await anext(iterator)
        await anext(iterator)

        listener.close()

        with pytest.raises(CDPEventListenerClosed):
            listener.put({3: 3})

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_create_iterator_after_close(self):
        listener = self.listener
        listener.put({1: 1})
        listener.close()
        iterator = aiter(listener)

        with pytest.raises(StopAsyncIteration):
            await anext(iterator)

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_anext_after_close(self):
        listener = self.listener
        iterator = aiter(listener)

        listener.put({1: 1})
        listener.put({2: 2})
        listener.put({3: 3})

        await anext(iterator)
        await anext(iterator)

        listener.close()

        with pytest.raises(StopAsyncIteration):
            await anext(iterator)

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_cancel_existing_task_before_put(self):
        listener = self.listener

        iterator = aiter(listener)
        task = anext(iterator)

        assert coroutine_might_block(task)

        listener.put({1: 1})
        listener.close()

        # The await statement should give the execution back to the reactor,
        # and execute the deferred callback first. After that, it will get
        # back to the task.
        assert await task == {1: 1}

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_concurrent_cancel_existing_task_before_put(self):
        listener = self.listener

        iterator = aiter(listener)
        task = anext(iterator)

        assert coroutine_might_block(task)

        def concurrent_function():
            listener.put({1: 1})
            listener.close()

        reactor.callLater(0, concurrent_function)

        assert await task == {1: 1}

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_garbage_collection(self):
        listener = self.listener

        iterator = aiter(listener)
        task = anext(iterator)

        assert coroutine_might_block(task)

        def concurrent_function():
            listener.put({1: 1})
            # When we call put, the event loop gives back execution to the
            #   await statement, which marks iterator to be garbage collected,
            #   which in turn, triggers the finally statement in the listener
            with pytest.raises(CDPEventListenerClosed):
                listener.put({2: 2})

        reactor.callLater(0, concurrent_function)

        await task

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_cancel_existing_task_after_put(self):
        listener = self.listener

        listener.put({1: 1})

        iterator = aiter(listener)
        task = anext(iterator)

        listener.close()

        with pytest.raises(StopAsyncIteration):
            await task

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_concurrent_cancel_existing_task_after_put(self):
        listener = self.listener

        listener.put({1: 1})

        iterator = aiter(listener)
        task = anext(iterator)

        def concurrent_function():
            listener.close()

        reactor.callLater(0, concurrent_function)

        assert await task == {1: 1}

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_multiple_anext(self):
        listener = self.listener
        iterator = aiter(listener)

        listener.put({1: 1})

        t1 = anext(iterator)
        t2 = anext(iterator)
        t3 = anext(iterator)

        listener.close()

        with pytest.raises(StopAsyncIteration):
            await t1
        with pytest.raises(StopAsyncIteration):
            await t2
        with pytest.raises(StopAsyncIteration):
            await t3

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_multiple_anext_concurrent_close(self):
        listener = self.listener
        iterator = aiter(listener)

        listener.put({1: 1})

        t1 = anext(iterator)
        t2 = anext(iterator)
        t3 = anext(iterator)

        def concurrent_function():
            listener.close()

        reactor.callLater(0, concurrent_function)

        assert await t1 == {1: 1}
        with pytest.raises(StopAsyncIteration):
            await t2
        with pytest.raises(StopAsyncIteration):
            await t3

    @timeoutDeferred(3)
    @pytest_twisted.ensureDeferred
    async def test_multiple_anext_concurrent_close_reverse(self):
        listener = self.listener
        iterator = aiter(listener)

        listener.put({1: 1})

        t1 = anext(iterator)
        t2 = anext(iterator)

        def concurrent_function():
            listener.close()

        reactor.callLater(0, concurrent_function)

        # order of await statement matters
        assert await t2 == {1: 1}
        with pytest.raises(StopAsyncIteration):
            await t1
