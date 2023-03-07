# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Websocket connection to the speaker.

The speaker normally listens on port 55001 for http requests containing
the api call. It is a simple http get request, where the path is the
complete request and header contains user information. The response of
the request is a http message where the body contains the information
in xml-format.
As long as you are connected to the speaker on this port, all requests
from other users of the speaker will be received, as well as all changes
of the speakers state.
"""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, Set

from pywam.lib.api_response import api_decode, api_error
from pywam.lib.http import build_http_header, parse_stream
from pywam.lib.validate import is_integer

if TYPE_CHECKING:
    from pywam.lib.api_call import ApiCall
    from pywam.lib.api_response import ApiResponse
    from pywam.lib.http import HttpResponse

_LOGGER = logging.getLogger(__name__)


class WamClient:
    """ Websocket connection to speaker.

    Arguments:
        ip:
            Speaker's IP address. (e.g "192.168.1.100")
        port:
            TCP port that speaker listens on.
        user:
            UUID for the connected user.
    """

    def __init__(self, ip: str, port: int, user: str) -> None:
        self._ip = ip
        self._port = port
        self._user = user
        # Socket
        self._connection_timeout: int = 5
        self._event_reader: asyncio.StreamReader | None = None
        self._event_writer: asyncio.StreamWriter | None = None
        self._connecting: bool = False
        self._disconnected: asyncio.Future | None = None
        # Events listener
        self._listening: bool = False
        self._listener_task: asyncio.Task | None = None
        # Event and response handling
        self._subscribers: Set[Callable] = set()
        self._response_queue: asyncio.Queue[ApiResponse] | None = None
        # API requests
        self._http_request: str = build_http_header(ip, port, user)
        self._request_timeout: int = 5

    @property
    def is_listening(self) -> bool:
        """ Returns true when listening for speaker events."""
        if self._listening and self._listener_task:
            return True
        else:
            return False

    @property
    def is_connected(self) -> bool:
        """ Returns true when connected to the speaker."""
        if self._event_reader and self._event_writer:
            return True
        else:
            return False

    @property
    def connection_timeout(self) -> int:
        return self._connection_timeout

    @connection_timeout.setter
    def connection_timeout(self, timeout: int) -> None:
        is_integer(timeout, (5, 60))
        self._connection_timeout = timeout

    @property
    def request_timeout(self) -> int:
        return self._request_timeout

    @request_timeout.setter
    def request_timeout(self, timeout: int) -> None:
        is_integer(timeout, (5, 60))
        self._request_timeout = timeout

    async def is_disconnected(self) -> None:
        """ Returns when disconnected.

        Can be used for auto reconnect to speaker when connection is
        lost. After calling :meth:`WamClient.connect()` this coroutine
        can be awaited for waiting for a lost connection.

        Returns:
            (None) When connection is lost to the speaker.

        Raises:
            Exemption that caused the connection to go down.
        """
        if self._disconnected and not self._disconnected.done():
            await self._disconnected

    async def connect(self) -> None:
        """ Connect to speaker.

        Raises:
            ConnectionError: If connection is not established.
        """
        # Make sure only one .connect() is running.
        if self._connecting:
            raise ConnectionError('Already trying to connect to speaker.')
        if self.is_connected:
            raise ConnectionError('Already connected to speaker.')
        if self._disconnected and not self._disconnected.done():
            raise ConnectionError('Already connected to speaker.')

        self._connecting = True

        if self._event_reader or self._event_writer:
            await self.disconnect()

        loop = asyncio.get_running_loop()
        self._disconnected = loop.create_future()

        try:
            self._event_reader, self._event_writer = await asyncio.wait_for(
                asyncio.open_connection(self._ip, self._port),
                timeout=self.connection_timeout,
            )
        except asyncio.TimeoutError:
            await self.disconnect()
            raise ConnectionError('Timeout when trying to connect to speaker.')
        except Exception as e:
            await self.disconnect()
            raise ConnectionError('Could not connect to speaker: %r', e)
        finally:
            self._connecting = False

    async def start_listening(self) -> None:
        """ Start listen to events from the speaker. """
        if not self.is_connected:
            raise ConnectionError('Not connected to the speaker.')
        if self._listener_task:
            await self.stop_listening()
        self._listener_task = asyncio.create_task(self._receive_loop())

    async def disconnect(self):
        """ Disconnect from speaker. """
        try:
            await self.stop_listening()
        except Exception:
            pass

        if self._event_writer:
            try:
                self._event_writer.close()
                await self._event_writer.wait_closed()
            except Exception:
                _LOGGER.exception('Unhandled exception when disconnecting.')

        self._reader, self._writer = None, None

        if self._disconnected and not self._disconnected.done():
            self._disconnected.set_result(None)

    async def stop_listening(self):
        """ Stop listen to events from the speaker. """
        if self._listener_task:
            try:
                self._listener_task.cancel()
                await self._listener_task
            except asyncio.CancelledError:
                pass
            except Exception:
                _LOGGER.exception('Unhandled exception when canceling listener task.')
            finally:
                self._listener_task = None

    async def request(self, api_call: 'ApiCall') -> 'ApiResponse':
        """ Send API to the speaker.

        Arguments:
            api_call:
                ApiCall object to send to the speaker.

        Returns:
            ApiResponse object with the requested information.

        Raises:
            ConnectionError: If not connected to the speaker.
        """
        if not self._event_reader:
            raise ConnectionError('No connection with speaker.')

        # Make sure that a second call is not made until we receive a
        # correct answer or get time out on current call.
        while self._response_queue:
            await asyncio.sleep(1)
        self._response_queue = asyncio.Queue(1)

        # Start a writer
        # We need to use new StreamWriter at every call to not get EOF
        # in the StreamReader used for listening for events. This could
        # probably be solved by writing a custom protocol in the future,
        # but is not prioritized at the moment.
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(self._ip, self._port),
                timeout=self.connection_timeout,
            )
        except asyncio.TimeoutError:
            await self.disconnect()
            raise ConnectionError('Timeout when trying to connect to speaker.')
        except Exception as e:
            await self.disconnect()
            raise ConnectionError('Could not connect to speaker: %r', e)

        # Send to the speaker.
        request = f'GET {api_call.url}{self._http_request}'
        writer.write(request.encode())
        await writer.drain()

        # Wait for correct response.
        try:
            response = await asyncio.wait_for(
                self._wait_for_response(api_call),
                timeout=self._request_timeout * api_call.timeout_multiple)
        except asyncio.TimeoutError:
            _LOGGER.info('Time out for api call: %s', api_call.method)
            response = api_error('Time out for api call')
        except Exception as e:
            _LOGGER.exception('Error while waiting for response')
            raise e
        finally:
            # Reset writer and queue
            writer.close()
            await writer.wait_closed()
            self._response_queue = None

        return response

    async def _receive_loop_error(self, msg: str) -> None:
        """ Error handling for receive loop. """
        self._listening = False
        if msg:
            _LOGGER.error(msg)
        try:
            await self.disconnect()
        except Exception:
            pass

    async def _receive_loop(self) -> None:
        """ Listen for api responses from the speaker.

        This method should be run as a asyncio task for receiving
        responses (events and api requests) from the speaker.
        """
        buffer: bytes = b''
        while True:
            try:
                # If there is a problem with the StreamReader we need
                # to disconnect, so that the user gets alerted of this.
                if not self._event_reader:
                    await self._receive_loop_error('Lost connection to speaker.')
                    break

                self._listening = True
                data = await self._event_reader.read(1024)
                # If we receive an empty byte something is wrong!
                if not data:
                    await self._receive_loop_error('Received EOF')
                _LOGGER.debug('Receiving data:')
                _LOGGER.debug(data)
                data = buffer + data
                http_responses = parse_stream(data)
                for http_response in http_responses:
                    if http_response.body:
                        await self._response_handler(http_response)
                    buffer = http_response.remainder

            except asyncio.CancelledError:
                _LOGGER.debug('Receive loop is cancelled.')
                self._listening = False
                raise
            except Exception:
                _LOGGER.exception('Error while reading stream')
                await self._receive_loop_error('')

    async def _response_handler(self, http_response: 'HttpResponse') -> None:
        """ Handles incoming HTTP responses.

        Incoming http responses (XML) get parsed to ApiResponse objects.
        The ApiResponse object is then dispatched to any subscriber,
        and returned to the request method.

        Arguments:
            http_response:
                HttpResponse object containing an response from the
                speaker.
        """
        try:
            api_response = api_decode(http_response.body)
        except Exception as e:
            api_response = api_error('ApiDecodingError', e, http_response.body)
            _LOGGER.warning('Error when decoding api response')
        self._dispatch_event(api_response)
        await self._return_response(api_response)

    async def _return_response(self, api_response: 'ApiResponse') -> None:
        """ Return the ApiResponse.

        If the request method is awaiting a response the ApiResponse
        object is put in a queue so that it can be returned to the
        caller.

        Argument:
            api_response:
                ApiResponse object to be returned to caller.
        """
        if self._response_queue:
            _LOGGER.debug('Queueing api response.')
            await self._response_queue.put(api_response)

    async def _wait_for_response(self, api_call: 'ApiCall') -> 'ApiResponse':
        """ Waits for the correct response from speaker.

        Argument:
            api_call:
                ApiCall object that was sent to the speaker

        Returns:
            ApiResponse that was requested.

        Raises:
            RuntimeError: If there is no asyncio queue to put the
                response in.
        """
        if not self._response_queue:
            raise RuntimeError('asyncio.Queue not initialized.')
        while True:
            api_response = await self._response_queue.get()
            if api_response.method != api_call.expected_response:
                continue
            if not api_call.user_check:
                return api_response
            else:
                if api_response.user == self._user:
                    return api_response

    # ******************************************************************
    # Observation methods
    # ******************************************************************

    def _dispatch_event(self, api_response: 'ApiResponse') -> None:
        """ Send events to subscriber.

        Arguments:
            api_response:
                Response from speaker to send to subscriber.
        """
        _LOGGER.debug('Sending api response to event listeners.')
        for subscriber in self._subscribers:
            try:
                subscriber(api_response)
            except Exception:
                _LOGGER.exception('Error when trying to dispatch an event')

    def register_subscriber(self, callback: Callable[['ApiResponse'], Any]) -> None:
        """ Register a function for receiving events from speaker.

        Arguments:
            callback:
                Callable that takes one argument to be called when an
                event is received. The event is passed as the first
                argument.

        Raises:
            TypeError: If given argument is not a callable.
        """
        if not callable(callback):
            raise TypeError('Subscriber must be a callable.')
        self._subscribers.add(callback)

    def unregister_subscriber(self, callback: Callable) -> None:
        """ Unregister listener.

        Arguments:
            callback:
                Callable to be removed from list of event subscribers.
        """
        self._subscribers.discard(callback)
