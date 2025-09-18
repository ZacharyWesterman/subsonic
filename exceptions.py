class SessionError(Exception):
    """
    Exception raised for errors related to Subsonic sessions.

    Args:
        message (str): Description of the error.

    Example:
        raise SessionError("Invalid session token")
    """

    def __init__(self, message: str):
        super().__init__(f'Subsonic Error: {message}')


class ConnectionError(SessionError):
    """
    Exception raised for errors occurring during a connection attempt in a session.

    This exception is a subclass of SessionError and is used to indicate issues
    related to establishing or maintaining a connection.

    Attributes:
        None
    """


class ResponseError(SessionError):
    """
    Exception raised for errors in the response during a session.

    Inherits from:
        SessionError

    Use this exception to indicate that an error occurred while processing a response in a session.
    """
