from dataclasses import dataclass, field
from typing import Optional, Callable
from functools import cached_property

from .song import Song

@dataclass(frozen = True)
class Album:
	id: str
	parent: str
	isDir: bool
	title: str
	album: str
	artist: Optional[str]
	year: Optional[int]
	genre: Optional[str]
	coverArt: str
	playCount: int
	created: str

	_query: Callable = field(repr = False)
	_stream: Callable[[str], str] = field(repr = False)

	@cached_property
	def songs(self) -> list[Song]:
		items = self._query('getMusicDirectory', {
			'id': self.id,
		}).get('directory', {}).get('child', [])

		return [Song(**i, _stream = self._stream) for i in items]
