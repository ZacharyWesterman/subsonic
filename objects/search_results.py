from typing import Callable

from .song import Song
from .album import Album
from .artist import Artist

class SearchResults:
	def __init__(self, artist: list[dict], album: list[dict], song: list[dict], *, query: Callable) -> None:
		self.artists = [Artist(**i) for i in artist]
		self.albums = [Album(**i, _query = query) for i in album]
		self.songs = [Song(**i) for i in song]

	def __repr__(self) -> str:
		return f'SearchResults(artists=[...{len(self.artists)}], albums=[...{len(self.albums)}], songs=[...{len(self.songs)}])'
