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
    coverArt: str
    size: int
    contentType: str
    suffix: str
    duration: int
    bitRate: int
    path: str
    isVideo: bool
    playCount: int
    created: datetime
    albumId: str
    type: str

    _stream: Callable[[str], str] = field(repr=False)

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
