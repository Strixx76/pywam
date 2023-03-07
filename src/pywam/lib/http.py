# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Module for http handling. """

import re
from typing import (
    Iterator,
    Optional,
    Pattern,
)


STATUS_LINE: Pattern = re.compile(rb'(HTTP/1.1 )(\d{3})([ ]?\w*)', re.MULTILINE)
CONTENT_LENGTH: Pattern = re.compile(rb'^Content-Length: (\d+)', re.MULTILINE)


class HttpResponse:
    """ Class for storing http responses.

    Attributes:
        status (opt):
            HTTP Status code.
        body (opt):
            HTTP body.
        remainder (opt):
            Data that belongs to next response.

    """
    __slots__ = ('status', 'body', 'remainder')

    def __init__(self,
                 status: Optional[int] = None,
                 body: str = '',
                 remainder: bytes = b'',
                 ) -> None:
        """ Initialize HttpResponse. """
        self.status = status
        self.body = body
        self.remainder = remainder


def parse_stream(data: bytes) -> Iterator[HttpResponse]:
    """ Parse Samsung WAM http responses from a socket stream.

    We can't do normal parsing since there is no EOF or even linebreaks
    between messages. So we need to rely on either Content-Length or
    split on status line, or both.
    This module uses both. It splits on status line and then checks
    content length to minimize the risk of bad responses due to chunked
    bodies.

    Arguments:
        data:
            Raw bytes from socket stream.

    Yields:
        :class:`HttpResponse` with parsed http messages.
    """
    while data:
        # Find the beginning of the http response.
        # Status line, should always be the first line:
        # https://tools.ietf.org/html/rfc2616#section-6.1
        first_split = STATUS_LINE.split(data)
        if len(first_split) < 5:
            # No complete status line
            yield HttpResponse(None, '', data)
            return
        status = int(first_split[2])
        if status != 200:
            data = b''.join(first_split[4:])
            continue

        # Split header and body
        parts = first_split[4].split(b'\r\n\r\n')
        if not len(parts) == 2:
            if len(first_split) > 5:
                # There was a incomplete response
                data = b''.join(first_split[5:])
                continue
            else:
                # Message is not complete and there should be more to come
                yield HttpResponse(None, '', data)
                return

        # Check that body is parsable
        re_cl = CONTENT_LENGTH.search(parts[0])
        if re_cl:
            content_length = int(re_cl.group(1))
        else:
            data = b''.join(first_split[5:])
            yield HttpResponse(None, '', b'')
            continue

        # Parse body
        _charset = 'utf-8'
        if len(parts[1]) == content_length:
            # Body is complete
            try:
                body = parts[1].decode(_charset)
            except UnicodeError:
                body = parts[1].decode(_charset, 'ignore')
            data = b''.join(first_split[5:])
            yield HttpResponse(status, body, b'')
            continue

        elif len(parts[1]) < content_length:
            # Body is NOT complete
            if len(first_split) > 5:
                # There was a incomplete response
                data = b''.join(first_split[5:])
                continue
            else:
                # There should come more data
                yield HttpResponse(None, '', data)
                return

        else:
            # There is most probably the very first part of the next
            # response status line in this body.
            yield HttpResponse(None, '', data)
            return


def build_http_header(ip: str, port: int, user: str) -> str:
    """ Build raw http header.

    Builds the http header needed when sending HTTP GET messages to the
    speaker.

    ip:
        Speaker's IP address. (e.g "192.168.1.100")
    port:
        TCP port that speaker listens on.
    user:
        UUID for the connected user.

    Returns:
        HTTP header.
    """

    http_request = [' HTTP/1.1']
    http_request.append(f'Host: {ip}:{port}\r\n')
    http_request.append(f'mobileUUID: {user}')
    http_request.append('mobileName: Wireless Audio')
    http_request.append('mobileVersion: 1.0')
    http_request.append('')

    return '\r\n'.join(http_request)
