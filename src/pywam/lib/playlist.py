# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Classes and function for handling playing url. """

from __future__ import annotations
from dataclasses import dataclass
import logging
import re
from urllib.parse import urlsplit

from pywam.lib.url import UrlMediaItem


_LOGGER = logging.getLogger(__name__)


M3U = 'M3U'
XM3U = 'Extended M3U'
PLS = 'PLS'
UNKNOWN = 'Unknown'

# https://www.iana.org/assignments/media-types/media-types.xhtml
PLAYLIST_MIME_TYPES = {
    'application/mpegurl': M3U,
    'application/x-mpegurl': M3U,
    'audio/mpegurl': M3U,
    'audio/x-mpegurl': M3U,
    'application/vnd.apple.mpegurl': M3U,
    'application/vnd.apple.mpegurl.audio': M3U,
    'audio/x-scpls': PLS,
    'text/html': UNKNOWN,
}

PLS_FILE: re.Pattern = re.compile(r'^File(\d+)=(.*)', re.IGNORECASE)
PLS_TITLE: re.Pattern = re.compile(r'^Title(\d+)=(.*)', re.IGNORECASE)
PLS_LENGTH: re.Pattern = re.compile(r'^Length(\d+)=(.*)', re.IGNORECASE)


@dataclass
class PlaylistRow:
    """ Stores rows in playlists. """
    file: str
    title: str
    length: str


def parse_playlist(playlist: str, mime_type: str | None = None) -> list[UrlMediaItem]:
    """ Parse a playlist and return first item as UrlMediaItem.

    Arguments:
        playlist:
            Playlist to parse.
        mime_type (optional):
            Format of the playlist. If left out we will try to guess it.

    Returns:
        Playlist as list of UrlMediaItem.
    """
    if mime_type is None:
        list_format = _find_playlist_format(playlist)
        if list_format == UNKNOWN:
            raise TypeError("Unknown playlist format")
    else:
        list_format = PLAYLIST_MIME_TYPES[mime_type]

    if list_format == M3U or list_format == XM3U:
        _LOGGER.debug("Parsing M3U playlist")
        parsed = m3u_parser(playlist)
    elif list_format == PLS:
        _LOGGER.debug("Parsing PLS playlist")
        parsed = pls_parser(playlist)

    return [UrlMediaItem(url=item.file, title=item.title, duration=item.length) for item in parsed]


def _find_playlist_format(playlist: str) -> str:
    """ Try to find out format of the playlist.

    Arguments:
        playlist:
            Playlist to find format of.

    Returns:
        One of the following constants: M3U , XM3U or PLS
        or UNKNOWN if not a playlist.
    """
    first_line = playlist.split(maxsplit=1)[0]

    # XM3U
    if first_line.startswith('#EXTM3U'):
        return XM3U
    # PLS
    if first_line.startswith('[playlist]'):
        return PLS
    # M3U
    test = urlsplit(first_line)
    # If first line looks like an valid url it is a m3u-playlist
    if test.scheme in ['http', 'https'] and test.netloc != '':
        return M3U

    return UNKNOWN


def pls_parser(pls: str) -> list[PlaylistRow]:
    """ Parse PLS-playlist.

    Supports PLS playlists.
    https://schworak.com/blog/e41/extended-pls-plsv2/
    https://en.wikipedia.org/wiki/PLS_(file_format)

    Arguments:
        pls:
            pls-formatted playlist as string.

    Returns:
        A list of dictionaries with the parsed playlist.
    """
    # Streamline line brakes and remove empty lines.
    fixed_list = pls.replace('\r\n', '\n')
    pls_lines = [line for line in fixed_list.split('\n') if line != '']

    # Header should always be [playlist].
    if pls_lines[0].lower() == '[playlist]':
        pls_lines.pop(0)
    else:
        raise TypeError('Not a valid PLS playlist')

    item_number = 1
    file, title, length = ('', '', '')
    number_of_entries, version = (None, None)
    playlist = []

    for line in pls_lines:

        rx_file = PLS_FILE.search(line)
        # First file row in a block
        if rx_file and not file:
            # If the number doesn't match leave loop
            if not int(rx_file.group(1)) == item_number:
                raise TypeError('Playlist items not in correct order')
            file = rx_file.group(2).strip()
            continue
        # New file row
        if rx_file and file:
            # Store previous block
            playlist.append(PlaylistRow(file, title, length))
            # Start new block
            file = rx_file.group(2).strip()
            title, length = ('', '')
            item_number += 1
            continue
        # A block should always start with File statement
        if not file:
            continue

        rx_title = PLS_TITLE.search(line)
        if rx_title:
            # If the number doesn't match leave loop
            if not int(rx_title.group(1)) == item_number:
                raise TypeError('Playlist items not in correct order')
            title = rx_title.group(2).strip()
            continue

        rx_length = PLS_TITLE.search(line)
        if rx_length:
            # If the number doesn't match leave loop
            if not int(rx_length.group(1)) == item_number:
                raise TypeError('Playlist items not in correct order')
            length = rx_length.group(2).strip()
            continue

        # Valid footers are 'NumberOfEntries' and 'Version'
        if line.lower().startswith('NumberOfEntries'):
            if number_of_entries:
                raise TypeError('NumberOfEntries occurs more than once')
            number_of_entries = int(line.rsplit('=')[0])
        if line.lower() == 'Version':
            if version:
                raise TypeError('Version occurs mote than once')
            version = int(line.rsplit('=')[0])

        # File should end after footers
        if number_of_entries and version:
            break

    # Store last iteration
    if file:
        playlist.append(PlaylistRow(file, title, length))
        item_number += 1

    # Check if correct number of entries.
    if number_of_entries:
        if number_of_entries != (item_number - 1):
            raise TypeError('Number of entries mismatch')

    return playlist


def m3u_parser(m3u: str) -> list[PlaylistRow]:
    """ Parse m3u playlist.

    Supports legacy m3u,extended m3u and m3u8.
    https://tools.ietf.org/html/rfc8216
    https://en.wikipedia.org/wiki/M3U

    Arguments:
        m3u:
            m3u-formatted playlist as string.

    Returns:
        List of items in the playlist
    """

    # Lines in a Playlist file are terminated by either a single line feed
    # character (\n) or a carriage return character followed by a line feed
    # character (\r\n). Each line is a URI, is blank, or starts with the
    # character '#'.  Blank lines are ignored.  Whitespace MUST NOT be
    # present, except for elements in which it is explicitly specified.
    fixed_list = m3u.replace('\r\n', '\n')
    m3u_lines = [line for line in fixed_list.split('\n') if line != '']

    # The EXTM3U tag indicates that the file is an Extended M3U [M3U]
    # Playlist file.  It MUST be the first line of every Media Playlist and
    # every Master Playlist. Its format is: '#EXTM3U'
    if m3u_lines[0].upper() == '#EXTM3U':
        # This is a Extended m3u
        m3u_lines.pop(0)

    title, duration = ('', '')
    playlist = []

    for line in m3u_lines:
        # The EXTINF tag specifies the duration of a Media Segment.  It applies
        # only to the next Media Segment.  This tag is REQUIRED for each Media
        # Segment.  Its format is: #EXTINF:<duration>,[<title>] where duration
        # is a decimal-floating-point or decimal-integer number that specifies
        # the duration of the Media Segment in seconds. The remainder of the line
        # following the comma is an optional human readable informative title of
        # the Media Segment expressed as UTF-8 text.
        if line.startswith('#EXTINF:'):
            extinf = line[8:].split(',', 1)
            duration = extinf[0]
            title = extinf[1]
            continue

        # Lines that start with the character '#' are either comments or tags.
        # Tags begin with #EXT. They are case sensitive. All other lines that
        # begin with '#' are comments and SHOULD be ignored.
        if line.startswith('#'):
            # Skip all comments
            continue
        else:
            # Only add items with plausible url to the playlist.
            test = urlsplit(line)
            if test.scheme in ['http', 'https'] and test.netloc != '':
                playlist.append(PlaylistRow(line, title, duration))
                title, duration = ('', '')

    return playlist
