class SessionError(Exception):
    def __init__(self, message: str):
        super().__init__(f'Subsonic Error: {message}')


class ConnectionError(SessionError):
    pass


class ResponseError(SessionError):
    pass
