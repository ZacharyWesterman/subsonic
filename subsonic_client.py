import random
import hashlib
import requests
import urllib
import json
from functools import lru_cache, cached_property
from typing import Callable

from .exceptions import *
from .objects import *


def _get_subsonic_query_func(connection_uri: str, rest_params: str) -> Callable:
    def query(action: str, parameters: dict = {}, *, process: bool = True) -> str | dict:
        url = f'{connection_uri}/rest/{action}.view?{rest_params}'
        for p in parameters:
            if parameters[p] is not None:
                url += f'&{p}={urllib.parse.quote_plus(str(parameters[p]))}'

        try:
            res = requests.get(url, timeout=31)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(e)
        except requests.exceptions.Timeout:
            raise ConnectionError('Connection timed out.')

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
                f'Unexpected response from server caused KeyError: {e}')

    return query


def _get_subsonic_stream_link_func(connection_uri: str, rest_params: str) -> Callable:
    return lambda song_id: f'{connection_uri}/rest/stream?id={song_id}&{rest_params}'


class SubsonicClient:
    def __init__(self, host: str, username: str, password: str, *, client: str = 'subsonic-py', version: str = '1.15.0') -> None:
        # random 32 digit hex string
        salt = ('%32x' % random.randrange(16**32)).strip()

        # Note that the password you pass in depends on how the credentials are stored on the server side!
        # E.g. if it's stored in plaintext, pass in the plain text password
        # however, if the encoder is MD5, pass in the md5sum to this function, NOT the plaintext password!
        md5sum = hashlib.md5((password + salt).encode('utf-8')).hexdigest()

        self.rest_params = f'u={username}&t={md5sum}&s={
            salt}&c={client}&v={version}&f=json'
        self.connection_uri = host

    def query(self, action, parameters: dict = {}, *, process: bool = True) -> str | dict:
        return _get_subsonic_query_func(self.connection_uri, self.rest_params)(action, parameters, process=process)

    def ping(self) -> dict:
        try:
            return Ping(**self.query('ping'))
        except ConnectionError:
            return Ping('failed', 'unknown', 'unknown')

    @lru_cache
    def search(self, text: str, *, artist_count: int | None = None, artist_offset: int | None = None, album_count: int | None = None, album_offset: int | None = None, song_count: int | None = None, song_offset: int | None = None, music_folder_id: int | None = None) -> SearchResults:
        data = self.query('search2', {
            'query': text,
            'artistCount': artist_count,
            'artistOffset': artist_offset,
            'albumCount': album_count,
            'albumOffset': album_offset,
            'songCount': song_count,
            'songOffset': song_offset,
            'musicFolderId': music_folder_id,
        }).get('searchResult2')

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
        items = self.query('getPlaylists').get(
            'playlists', {}).get('playlist', [])

        return [
            Playlist(
                **i,
                _query=_get_subsonic_query_func(
                    self.connection_uri, self.rest_params),
                _stream=_get_subsonic_stream_link_func(
                    self.connection_uri, self.rest_params)
            ) for i in items]

    def playlist(self, name: str) -> Playlist | None:
        for i in self.playlists:
            if i.name == name:
                return i

        return None

    @cached_property
    def license(self) -> str:
        return self.query('getLicense').get('license', '')

    @cached_property
    def folders(self) -> dict[str, str]:
        items = self.query('getMusicFolders').get(
            'musicFolders', {}).get('musicFolder', [])

        return {
            i['name']: i['id'] for i in items
        }

    @lru_cache
    def albums(self, folder: str, page: int, count: int = 40) -> list:
        folder_id = self.folders.get(folder)
        if folder_id is None:
            raise ResponseError(f'Folder "{folder}" does not exist.')

        items = self.query('getAlbumList', {
            'type': 'alphabeticalByName',
            'size': count,
            'offset': page * count,
            'musicFolderId': folder_id,
        }).get('albumList', {}).get('album', [])

        return [
            Album(
                **i,
                _query=_get_subsonic_query_func(
                    self.connection_uri, self.rest_params),
                _stream=_get_subsonic_stream_link_func(
                    self.connection_uri, self.rest_params)
            ) for i in items]

    @lru_cache
    def album(self, album_id: str) -> Album:
        data = self.query('getAlbum', {
            'id': album_id,
        }).get('album')

        return Album(
            **data,
            _query=_get_subsonic_query_func(
                self.connection_uri, self.rest_params),
            _stream=_get_subsonic_stream_link_func(
                self.connection_uri, self.rest_params)
        )
