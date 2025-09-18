"""Subsonic API Search Results Object"""

from typing import Callable

from .album import Album
from .artist import Artist
from .song import Song


class SearchResults:
    """
    Represents the results of a search, containing lists of artists, albums, and songs.

    Args:
        artist (list[dict]): List of dictionaries representing artist data.
        album (list[dict]): List of dictionaries representing album data.
        song (list[dict]): List of dictionaries representing song data.
        query (Callable): A callable used for querying additional data (passed to Album).
        stream (Callable): A callable used for streaming data (passed to Album and Song).

    Attributes:
        artists (list[Artist]): List of Artist objects created from the input data.
        albums (list[Album]): List of Album objects created from the input data,
            with query and stream callables.
        songs (list[Song]): List of Song objects created from the input data, with stream callable.

    Methods:
        __repr__(): Returns a string representation of the SearchResults object,
            showing counts of artists, albums, and songs.
    """

    def __init__(
        self,
        artist: list[dict],
        album: list[dict],
        song: list[dict],
        *,
        query: Callable,
        stream: Callable
    ) -> None:
        self.artists = [Artist(**i) for i in artist]
        self.albums = [Album(**i, _query=query, _stream=stream) for i in album]
        self.songs = [Song(**i, _stream=stream) for i in song]

    def __repr__(self) -> str:
        return (
            f'SearchResults(artists=[...{len(self.artists)}], ' +
            f'albums=[...{len(self.albums)}], songs=[...{len(self.songs)}])'
        )
