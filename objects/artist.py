"""Subsonic API Artist Object"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Artist:
    """
    Represents a musical artist.

    Attributes:
        id (str): Unique identifier for the artist.
        name (str): Name of the artist.
    """

    id: str
    name: str
