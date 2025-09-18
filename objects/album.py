"""Subsonic API Album Object"""

import base64
from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable, Optional

from .song import Song

_album_art_cache: dict[str, str] = {}


@dataclass(frozen=True)
class Album:
    """
    Represents a music album with metadata and related operations.

    Attributes:
        id (str): Unique identifier for the album.
        isDir (bool): Indicates if the album is a directory.
        title (str): Title of the album.
        album (str): Album name.
        playCount (int): Number of times the album has been played.
        created (str): Creation date of the album.
        artist (Optional[str]): Name of the artist.
        year (Optional[int]): Release year of the album.
        genre (Optional[str]): Genre of the album.
        coverArt (Optional[str]): Identifier for the album's cover art.
        averageRating (Optional[float]): Average user rating of the album.
        parent (Optional[str]): Identifier of the parent directory or album.

    Methods:
        songs (list[Song]): Returns a list of Song objects in the album, fetched via API.
        cover (str): Returns the base64-encoded cover art for the album, caching results for efficiency.
    """

    id: str
    isDir: bool
    title: str
    album: str
    playCount: int
    created: str

    _query: Callable = field(repr=False)
    _stream: Callable[[str], str] = field(repr=False)

    artist: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    coverArt: Optional[str] = None
    averageRating: Optional[float] = None
    parent: Optional[str] = None

    @cached_property
    def songs(self) -> list[Song]:
        """
        Retrieves a list of Song objects associated with the album.

        Returns:
            list[Song]: A list of Song instances representing the songs in the album.
        """
        items = self._query('getMusicDirectory', {
            'id': self.id,
        }).get('directory', {}).get('child', [])

        return [Song(**i, _stream=self._stream) for i in items]

    @property
    def cover(self) -> str:
        """
        Retrieves the album cover art as a base64-encoded string.

        If the cover art is not already cached, it queries for the cover art data,
        encodes it in base64, and stores it in the cache. Returns the cached
        base64-encoded cover art string, or an empty string if not available.

        Returns:
            str: The base64-encoded cover art string, or an empty string if not found.
        """

        if self.coverArt and self.coverArt not in _album_art_cache:
            data = self._query('getCoverArt', {
                'id': self.id,
                'size': 160,
            }, process=False)

            _album_art_cache[self.coverArt] = base64.b64encode(data).decode()

        return _album_art_cache.get(self.coverArt, '')  # type: ignore
