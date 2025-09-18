"""Subsonic API Playlist Object"""

from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable, Optional

from .song import Song


@dataclass(frozen=True)
class Playlist:
    """
    Represents a music playlist with metadata and song entries.

    Attributes:
        id (str): Unique identifier for the playlist.
        name (str): Name of the playlist.
        comment (str): Optional comment or description.
        owner (str): Username of the playlist owner.
        public (bool): Indicates if the playlist is public.
        songCount (int): Number of songs in the playlist.
        duration (int): Total duration of the playlist in seconds.
        created (str): Creation timestamp of the playlist.
        coverArt (str): Identifier for the playlist's cover art.
        changed (Optional[str]): Timestamp of the last modification.
        entry (Optional[list]): Raw song entry data for the playlist.

    Methods:
        songs -> list[Song]: Returns a list of Song objects in the playlist.
            If entries are not cached, fetches them using the provided query callable.
    """

    id: str
    name: str
    comment: str
    owner: str
    public: bool
    songCount: int
    duration: int
    created: str
    coverArt: str

    _query: Callable = field(repr=False)
    _stream: Callable[[str], str] = field(repr=False)

    changed: Optional[str] = None
    entry: Optional[list] = None

    @cached_property
    def songs(self) -> list[Song]:
        """
        Retrieves a list of Song objects associated with the playlist.

        If the playlist entries are not already loaded, it queries the backend for the playlist data
        using the playlist ID and extracts the entries. Otherwise, it uses the existing entries.

        Returns:
            list[Song]: A list of Song objects representing the songs in the playlist.
        """

        if not self.entry:
            items = self._query('getPlaylist', {'id': self.id}).get(
                'playlist', {}).get('entry', [])
        else:
            items = self.entry

        return [
            Song(
                **i,
                _stream=self._stream
            )
            for i in items
        ]
