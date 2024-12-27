from dataclasses import dataclass, field
from typing import Optional, Callable
from functools import cached_property
import base64

from .song import Song

_album_art_cache: dict[str, str] = {}


@dataclass(frozen=True)
class Album:
    id: str
    parent: str
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

    @cached_property
    def songs(self) -> list[Song]:
        items = self._query('getMusicDirectory', {
            'id': self.id,
        }).get('directory', {}).get('child', [])

        return [Song(**i, _stream=self._stream) for i in items]

    @property
    def cover(self) -> str:
        if self.coverArt and self.coverArt not in _album_art_cache:
            data = self._query('getCoverArt', {
                'id': self.id,
                'size': 160,
            }, process=False)

            _album_art_cache[self.coverArt] = base64.b64encode(data).decode()

        return _album_art_cache.get(self.coverArt, '')
