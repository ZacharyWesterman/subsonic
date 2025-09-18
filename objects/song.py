"""Subsonic API Song Object"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional


@dataclass(frozen=True)
class Song:
    """
    Represents a song object with metadata and streaming capabilities.

    Attributes:
        id (str): Unique identifier for the song.
        parent (str): Identifier of the parent directory or collection.
        isDir (bool): Indicates if the object is a directory.
        title (str): Title of the song.
        album (str): Album name the song belongs to.
        playCount (int): Number of times the song has been played.
        created (datetime): Date and time when the song was created.
        size (int): Size of the song file in bytes.
        contentType (str): MIME type of the song file.
        suffix (str): File extension of the song.
        duration (int): Duration of the song in seconds.
        bitRate (int): Bitrate of the song in kbps.
        path (str): Filesystem path to the song.
        isVideo (bool): Indicates if the file is a video.
        albumId (str): Identifier for the album.
        type (str): Type of media (default is 'music').
        coverArt (Optional[str]): Identifier or path to the cover art image.
        artist (Optional[str]): Name of the artist.
        artistId (Optional[str]): Identifier for the artist.
        track (Optional[int]): Track number in the album.
        year (Optional[int]): Year of release.
        genre (Optional[str]): Genre of the song.
        discNumber (Optional[int]): Disc number in a multi-disc album.
        transcodedContentType (Optional[str]): MIME type of the transcoded file.
        transcodedSuffix (Optional[str]): File extension of the transcoded file.
        averageRating (Optional[str]): Average user rating for the song.

    Properties:
        uri (str): Returns the streaming URI for the song using the provided stream function.

    Private Attributes:
        _stream (Callable[[str], str]): Function to generate a streaming URI for the song.
    """

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
    albumId: str = '0'
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
    averageRating: Optional[str] = None

    @property
    def uri(self) -> str:
        return self._stream(self.id)
