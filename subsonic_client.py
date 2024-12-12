import random, hashlib, requests, urllib, json
from functools import lru_cache
from typing import Callable

from .exceptions import *
from .objects import *

def _get_subsonic_query_func(connection_uri: str, rest_params: str) -> Callable:
	def query(action: str, parameters: dict = {}, *, process: bool = True) -> str|dict:
		url = f'{connection_uri}/rest/{action}.view?{rest_params}'
		for p in parameters:
			if parameters[p] is not None:
				url += f'&{p}={urllib.parse.quote_plus(str(parameters[p]))}'

		try:
			res = requests.get(url, timeout = 31)
		except requests.exceptions.ConnectionError as e:
			raise ConnectionError(e)
		except requests.exceptions.Timeout:
			raise ConnectionError('Connection timed out.')

		if res.status_code >= 300 or res.status_code < 200:
			raise ConnectionError(f'Failed to connect to server (code {res.status_code})')

		if not process:
			return res.content

		data = json.loads(res.text)

		try:
			if data['subsonic-response']['status'] != 'ok':
				raise ResponseError(data['subsonic-response']['error']['message'])

			return data['subsonic-response']
		except KeyError as e:
			raise ResponseError(f'Unexpected response from server caused KeyError: {e}')
		
	return query

class SubsonicClient:
	def __init__(self, host: str, username: str, password: str, *, client: str = 'subsonic-py', version: str = '1.15.0') -> None:
		salt = ('%32x' % random.randrange(16**32)).strip() #random 32 digit hex string

		# Note that the password you pass in depends on how the credentials are stored on the server side!
		# E.g. if it's stored in plaintext, pass in the plain text password
		# however, if the encoder is MD5, pass in the md5sum to this function, NOT the plaintext password!
		md5sum = hashlib.md5((password + salt).encode('utf-8')).hexdigest()

		self.rest_params = f'u={username}&t={md5sum}&s={salt}&c={client}&v={version}&f=json'
		self.connection_uri = host

	def query(self, action, parameters: dict = {}, *, process: bool = True) -> str|dict:
		return _get_subsonic_query_func(self.connection_uri, self.rest_params)(action, parameters, process = process)

	def ping(self) -> dict:
		try:
			return Ping(**self.query('ping'))
		except ConnectionError:
			return Ping('failed', 'unknown', 'unknown')

	def search(self, text: str, *, artist_count: int|None = None, artist_offset: int|None = None, album_count: int|None = None, album_offset: int|None = None, song_count: int|None = None, song_offset: int|None = None, music_folder_id: int|None = None) -> SearchResults:
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

		return SearchResults(
			**data,
			query = _get_subsonic_query_func(self.connection_uri, self.rest_params)
		)
