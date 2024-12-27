from dataclasses import dataclass, field
from typing import Optional, Callable
from datetime import datetime


@dataclass(frozen=True)
class Song:
    id: str
    parent: str
    isDir: bool
    title: str
    album: str
    playCount: int
    created: datetime

    _stream: Callable[[str], str] = field(repr=False)

    size: int = 0
    contentType: str = ''
    suffix: str = ''
    duration: int = 0
    bitRate: int = 0
    path: str = ''
    isVideo: bool = False
    albumId: str = 0
    type: str = 'music'

    coverArt: Optional[str] = None
    artist: Optional[str] = None
    artistId: Optional[str] = None
    track: Optional[int] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    discNumber: Optional[int] = None
    transcodedContentType: Optional[str] = None
    transcodedSuffix: Optional[str] = None

    @property
    def uri(self) -> str:
        return self._stream(self.id)
