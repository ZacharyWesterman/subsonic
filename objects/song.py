from dataclasses import dataclass, field
from typing import Optional, Callable
from datetime import datetime

@dataclass(frozen = True)
class Song:
	id: str
	parent: str
	isDir: bool
	title: str
	album: str
	artist: Optional[str]
	track: Optional[int]
	year: Optional[int]
	genre: Optional[str]
	coverArt: str
	size: int
	contentType: str
	suffix: str
	duration: int
	bitRate: int
	path: str
	isVideo: bool
	playCount: int
	discNumber: Optional[int]
	created: datetime
	albumId: str
	artistId: str
	type: str

	_stream: Callable[[str], str] = field(repr = False)

	@property
	def uri(self) -> str:
		return self._stream(self.id)
