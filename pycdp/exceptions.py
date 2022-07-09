

class CDPError(Exception):
    pass


class CDPBrowserError(CDPError):
    ''' This exception is raised when the browser's response to a command
    indicates that an error occurred. '''
    def __init__(self, obj):
        self.code: int = obj['code']
        self.message: str = obj['message']
        self.detail = obj.get('data')

    def __str__(self):
        return 'BrowserError<code={} message={}> {}'.format(self.code,
            self.message, self.detail)


class CDPConnectionClosed(CDPError):
    ''' Raised when a public method is called on a closed CDP connection. '''
    def __init__(self, reason):
        '''
        Constructor.
        :param reason:
        :type reason: wsproto.frame_protocol.CloseReason
        '''
        self.reason = reason

    def __repr__(self):
        ''' Return representation. '''
        return '{}<{}>'.format(self.__class__.__name__, self.reason)


class CDPSessionClosed(CDPError):
    pass


class CDPInternalError(CDPError):
    ''' This exception is only raised when there is faulty logic in TrioCDP or
    the integration with PyCDP. '''


class CDPEventListenerClosed(CDPError):
    pass