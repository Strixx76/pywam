# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Classes and function for handling playing url. """

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit


# https://www.iana.org/assignments/media-types/media-types.xhtml
SUPPORTED_MIME_TYPES = (
    'audio/aac',
    'audio/aacp',
    'audio/aiff',
    'audio/flac',
    'audio/mp4',
    'audio/mp4a-latm',
    'audio/MPA',
    'audio/mpa-robust',
    'audio/mpeg',
    'audio/mpeg4-generic',
    'audio/ogg',
    'audio/vnd.wave',
    'audio/vorbis',
    'audio/vorbis-config',
    'audio/wav',
    'audio/wave',
    'audio/x-aiff',
    'audio/x-flac',
    'audio/x-ms-wma',
    'audio/x-wav',
)


@dataclass
class UrlMediaItem:
    """ Representing a playable url stream.

    Arguments:
        url:
            url with a playable stream.
        title:
            Title of stream.
        description:
            Description for the stream.
        duration (optional):
            Duration in seconds.
        thumbnail (optional):
            Url to thumbnail.
    """

    def __init__(self,
                 url: str,
                 title: str = '',
                 description: str = '',
                 duration: str | None = None,
                 thumbnail: str | None = None
                 ) -> None:
        """ Initialize a UrlMediaItem. """
        self._url = url
        self._title = title
        self._description = description
        self._duration = duration
        self._thumbnail = thumbnail

    @property
    def url(self) -> str:
        """ Return url of media item. """
        return self._url

    @property
    def title(self) -> str:
        """ Return title of media item. """
        if self._title:
            return self._title

        title = 'URL stream'
        try:
            if (host := urlsplit(self._url).hostname) is not None:
                domain = ".".join(host.split('.')[-3:])
                title = domain.replace('www.', '')
        except Exception:
            pass

        return title

    @property
    def description(self) -> str:
        """ Return description of media item. """
        if self._description:
            return self._description

        description = 'URL stream'
        try:
            path = urlsplit(self._url).path
            file = path.split('/')[-1]
            if file:
                description = file
        except Exception:
            pass

        return description

    @property
    def duration(self) -> str | None:
        """ Return duration of media item in seconds. """
        return self._duration

    @property
    def thumbnail(self) -> str | None:
        """ Return thumbnail url of media item. """
        return self._thumbnail
