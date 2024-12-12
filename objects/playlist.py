from dataclasses import dataclass, field
from typing import Optional, Callable
from functools import cached_property

from .song import Song


@dataclass(frozen=True)
class Playlist:
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

    @cached_property
    def songs(self) -> list[Song]:
        items = self._query('getMusicDirectory', {
            'id': self.id,
        }).get('directory', {}).get('child', [])

        print(items)

        return [Song(**i, _stream=self._stream) for i in items]
