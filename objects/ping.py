"""Subsonic API Ping Object"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Ping:
    """
    Represents a ping response object with status, version, and type attributes.

    Attributes:
        status (str): The status of the ping response (e.g., 'ok').
        version (str): The version of the ping response.
        type (str): The type of the ping response.

    Properties:
        ok (bool): Returns True if the status is 'ok', otherwise False.
    """

    status: str
    version: str
    type: str

    @property
    def ok(self) -> bool:
        """
        Check if the status of the object is 'ok'.

        Returns:
            bool: True if the status is 'ok', False otherwise.
        """
        return self.status == 'ok'
