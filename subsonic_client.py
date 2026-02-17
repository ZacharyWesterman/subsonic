"""Subsonic API client implementation."""

import base64
import hashlib
import json
import random
from functools import cached_property, lru_cache
from typing import Any, Callable
from urllib.parse import quote_plus

import requests

from .exceptions import ConnectionError, ResponseError
from .objects import Album, Ping, Playlist, SearchResults, Song


def _get_subsonic_query_func(connection_uri: str, rest_params: str) -> Callable:
    def query(action: str, parameters: dict | None = None, *, process: bool = True) -> bytes | dict:

        url = f'{connection_uri}/rest/{action}.view?{rest_params}'
        if parameters:
            for p in parameters:
                if parameters[p] is not None:
                    url += f'&{p}={quote_plus(str(parameters[p]))}'

        try:
            res = requests.get(url, timeout=31)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(str(e)) from e
        except requests.exceptions.Timeout as e:
            raise ConnectionError('Connection timed out.') from e

        if res.status_code >= 300 or res.status_code < 200:
            raise ConnectionError(
                f'Failed to connect to server (code {res.status_code})')

        if not process:
            return res.content

        data = json.loads(res.text)

        try:
            if data['subsonic-response']['status'] != 'ok':
                raise ResponseError(
                    data['subsonic-response']['error']['message'])

            return data['subsonic-response']
        except KeyError as e:
            raise ResponseError(
                f'Unexpected response from server caused KeyError: {e}'
            ) from e

    return query


def _get_subsonic_stream_link_func(connection_uri: str, rest_params: str) -> Callable:
    return lambda song_id: f'{connection_uri}/rest/stream?id={song_id}&{rest_params}'


class SubsonicClient:
    """
    SubsonicClient provides an interface to interact with a Subsonic music server via its REST API.

    Args:
        host (str): The base URI of the Subsonic server.
        username (str): The username for authentication.
        password (str): The password or MD5 hash, depending on server configuration.
        client (str, optional): The client identifier. Defaults to 'subsonic-py'.
        version (str, optional): The Subsonic API version. Defaults to '1.15.0'.

    Attributes:
        rest_params (str): The REST API authentication and client parameters.
        connection_uri (str): The base URI for API requests.

    Methods:
        query(action, parameters={}, process=True) -> str | dict:
            Executes a generic Subsonic API query.

        ping() -> dict:
            Checks connectivity to the Subsonic server.

        search(
            text,
            artist_count=None,
            artist_offset=None,
            album_count=None,
            album_offset=None,
            song_count=None,
            song_offset=None,
            music_folder_id=None
        ) -> SearchResults:
            Searches for artists, albums, and songs matching the query text.

        playlists -> list[Playlist]:
            Returns a list of available playlists.

        playlist(name) -> Playlist | None:
            Retrieves a playlist by name.

        license -> str:
            Returns the license information for the Subsonic server.

        folders -> dict[str, str]:
            Returns a mapping of music folder names to their IDs.

        albums(folder, page, count=40) -> list:
            Retrieves a paginated list of albums from a specified music folder.

        album_songs(album_id) -> list[Song]:
            Retrieves the list of songs in a specified album.

        cover_art(cover_art_id) -> str:
            Retrieves the cover art for a given ID, encoded as a base64 string.
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        *,
        client: str = 'subsonic-py',
        version: str = '1.15.0'
    ) -> None:
        # random 32 digit hex string
        salt = ('%32x' % random.randrange(16**32)).strip()

        # Note that the password you pass in depends on how the credentials
        # are stored on the server side!
        # E.g. if it's stored in plaintext, pass in the plain text password
        # however, if the encoder is MD5, pass in the md5sum to this function,
        # NOT the plaintext password!
        md5sum = hashlib.md5((password + salt).encode('utf-8')).hexdigest()

        self.rest_params = f'u={username}&t={md5sum}&s={salt}&c={client}&v={version}&f=json'
        self.connection_uri = host

    def query(
        self,
        action,
        parameters: dict | None = None,
        *,
        process: bool = True
    ) -> bytes | dict[str, Any]:
        """
        Executes a query against the Subsonic API.
        Args:
            action (str): The API action to perform.
            parameters (dict, optional): Parameters to include in the query. Defaults to None.
            process (bool, optional): Whether to process the response. Defaults to True.
        Returns:
            bytes | dict: The response from the API, either as a raw string or a processed dictionary.
        """
        return _get_subsonic_query_func(
            self.connection_uri,
            self.rest_params
        )(action, parameters, process=process)

    def ping(self) -> Ping:
        """
        Sends a 'ping' request to the Subsonic server to check connectivity.

        Returns:
            Ping: An instance of Ping containing the server's response data.
                   If a ConnectionError occurs, returns a Ping object with
                   status 'failed' and unknown version and server values.
        """
        try:
            return Ping(**self.query('ping'))  # type: ignore
        except ConnectionError:
            return Ping('failed', 'unknown', 'unknown')

    @lru_cache
    def search(
        self,
        text: str,
        *,
        artist_count: int | None = None,
        artist_offset: int | None = None,
        album_count: int | None = None,
        album_offset: int | None = None,
        song_count: int | None = None,
        song_offset: int | None = None,
        music_folder_id: int | None = None
    ) -> SearchResults:
        """
        Searches for artists, albums, and songs matching the given text query.

        Args:
            text (str): The search query string.
            artist_count (int | None, optional): Maximum number of artists to return.
            artist_offset (int | None, optional): Offset for artist results (for pagination).
            album_count (int | None, optional): Maximum number of albums to return.
            album_offset (int | None, optional): Offset for album results (for pagination).
            song_count (int | None, optional): Maximum number of songs to return.
            song_offset (int | None, optional): Offset for song results (for pagination).
            music_folder_id (int | None, optional): ID of the music folder to restrict the search.

        Returns:
            SearchResults: An object containing the search results for artists, albums, and songs,
            along with helper functions for querying and streaming.
        """
        data: dict[str, Any] = self.query('search2', {
            'query': text,
            'artistCount': artist_count,
            'artistOffset': artist_offset,
            'albumCount': album_count,
            'albumOffset': album_offset,
            'songCount': song_count,
            'songOffset': song_offset,
            'musicFolderId': music_folder_id,
        }).get('searchResult2')  # type: ignore

        for i in ['song', 'album', 'artist']:
            if i not in data:
                data[i] = {}

        return SearchResults(
            **data,
            query=_get_subsonic_query_func(
                self.connection_uri, self.rest_params),
            stream=_get_subsonic_stream_link_func(
                self.connection_uri, self.rest_params)
        )

    @cached_property
    def playlists(self) -> list[Playlist]:
        """
        Retrieves a list of playlists from the Subsonic server.

        Returns:
            list[Playlist]: A list of Playlist objects, each initialized with
            data from the server response and helper functions for querying and streaming.

        The method sends a 'getPlaylists' query to the server, extracts the playlist data,
        and constructs Playlist instances with appropriate query and stream functions.
        """
        items = self.query('getPlaylists').get('playlists', {}).get('playlist', [])  # type: ignore

        return [
            Playlist(
                **i,
                _query=_get_subsonic_query_func(
                    self.connection_uri, self.rest_params),
                _stream=_get_subsonic_stream_link_func(
                    self.connection_uri, self.rest_params)
            ) for i in items]

    def playlist(self, name: str) -> Playlist | None:
        """
        Retrieves a playlist by its name.

        Args:
            name (str): The name of the playlist to retrieve.

        Returns:
            Playlist | None: The playlist object with the specified name if found, otherwise None.
        """
        for i in self.playlists:
            if i.name == name:
                return i

        return None

    @cached_property
    def license(self) -> str:
        """
        Retrieves the license information from the Subsonic server.

        Returns:
            str: The license string if available, otherwise an empty string.
        """
        return self.query('getLicense').get('license', '')  # type: ignore

    @cached_property
    def folders(self) -> dict[str, str]:
        """
        Retrieves a dictionary mapping music folder names to their corresponding IDs.

        Returns:
            dict[str, str]: A dictionary where the keys are folder names
                and the values are folder IDs.
        """
        items = self.query(
            'getMusicFolders'
        ).get('musicFolders', {}).get('musicFolder', [])  # type: ignore

        return {
            i['name']: i['id'] for i in items
        }

    @lru_cache
    def albums(self, folder: str, page: int, count: int = 40) -> list:
        """
        Retrieves a paginated list of albums from a specified music folder.

        Args:
            folder (str): The name of the music folder to retrieve albums from.
            page (int): The page number (zero-based) to retrieve.
            count (int, optional): The number of albums per page. Defaults to 40.

        Returns:
            list: A list of Album objects for the specified folder and page.

        Raises:
            ResponseError: If the specified folder does not exist.
        """
        folder_id = self.folders.get(folder)
        if folder_id is None:
            raise ResponseError(f'Folder "{folder}" does not exist.')

        items = self.query('getAlbumList', {
            'type': 'alphabeticalByName',
            'size': count,
            'offset': page * count,
            'musicFolderId': folder_id,
        }).get('albumList', {}).get('album', [])  # type: ignore

        return [
            Album(
                **i,
                _query=_get_subsonic_query_func(
                    self.connection_uri, self.rest_params),
                _stream=_get_subsonic_stream_link_func(
                    self.connection_uri, self.rest_params)
            ) for i in items]

    @lru_cache
    def album_songs(self, album_id: str) -> list[Song]:
        """
        Retrieves a list of songs from a specified album.

        Args:
            album_id (str): The unique identifier of the album.

        Returns:
            list[Song]: A list of Song objects representing the tracks in the album.
        """
        data = self.query('getMusicDirectory', {
            'id': album_id,
        }).get('directory', {}).get('child', [])  # type: ignore

        return [
            Song(
                **i,
                _stream=_get_subsonic_stream_link_func(
                    self.connection_uri, self.rest_params)
            )
            for i in data
        ]

    @lru_cache
    def cover_art(self, cover_art_id: str) -> str:
        """
        Retrieves the cover art image for the specified cover art ID,
        encodes it in base64, and returns it as a string.

        Args:
            cover_art_id (str): The unique identifier for the cover art to retrieve.

        Returns:
            str: The base64-encoded cover art image.

        Raises:
            Any exceptions raised by the `query` method or during base64 encoding.
        """
        data: bytes = self.query('getCoverArt', {
            'id': cover_art_id,
            'size': 160,
        }, process=False)  # type: ignore

        return base64.b64encode(data).decode()
