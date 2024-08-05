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

from pywam.lib.api_response import ApiResponse, api_decode, api_error
from pywam.lib.exceptions import ApiCallTimeoutError
from pywam.lib.http import build_http_header, parse_stream
from pywam.lib.validate import is_integer


if TYPE_CHECKING:
    from pywam.lib.api_call import ApiCall
    from pywam.lib.http import HttpResponse
    from pywam.speaker import Speaker

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

    def __init__(self, speaker: Speaker) -> None:
        self._ip = speaker.ip
        self._port = speaker.port
        self._user = speaker.user
        # Socket
        self._connection_timeout: int = 5
        self._event_reader: asyncio.StreamReader | None = None
        self._event_writer: asyncio.StreamWriter | None = None
        self._connecting: bool = False
        self._disconnecting: bool = False
        # Events listener
        self._listening: asyncio.Event = asyncio.Event()
        self._listener_task: asyncio.Task | None = None
        # Event and response handling
        self._subscribers: Set[Callable] = set()
        self._response_queue: asyncio.Queue[ApiResponse] | None = None
        # API requests
        self._http_request: str = build_http_header(self._ip, self._port, self._user)
        self._request_timeout: int = 10

    @property
    def is_connected(self) -> bool:
        """ Returns true when connected to the speaker. """
        if self._event_reader and self._event_writer:
            return True
        return False

    @property
    def is_listening(self) -> bool:
        """ Returns true when listening for responses from speaker. """
        return self._listening.is_set()

    @property
    def connection_timeout(self) -> int:
        """ Time out for connecting to speaker. """
        return self._connection_timeout

    @connection_timeout.setter
    def connection_timeout(self, timeout: int) -> None:
        is_integer(timeout, (5, 60))
        self._connection_timeout = timeout

    @property
    def request_timeout(self) -> int:
        """ Time out for sending API calls to speaker. """
        return self._request_timeout

    @request_timeout.setter
    def request_timeout(self, timeout: int) -> None:
        is_integer(timeout, (5, 60))
        self._request_timeout = timeout

    async def connect(self) -> None:
        """ Connect to speaker.

        Raises:
            ConnectionError: If connection is not established.
        """
        if self._connecting:
            raise ConnectionError('Already trying to connect to speaker')
        if self.is_connected:
            raise ConnectionError('Already connected to speaker')
        if self._disconnecting:
            raise ConnectionError('Waiting for speaker to disconnect')
        self._connecting = True

        try:
            self._event_reader, self._event_writer = await asyncio.wait_for(
                asyncio.open_connection(self._ip, self._port),
                timeout=self.connection_timeout,
            )
        except asyncio.TimeoutError as exc:
            await self.disconnect()
            raise ConnectionError('Timeout when trying to connect to speaker') from exc
        except Exception as exc:
            await self.disconnect()
            raise ConnectionError('Could not connect to speaker') from exc
        finally:
            self._connecting = False

    async def start_listening(self) -> None:
        """ Start listen to events from the speaker. """
        if not self.is_connected:
            raise ConnectionError('Not connected to the speaker')
        if self._listener_task:
            raise ConnectionError('Listener is already running')

        self._listener_task = asyncio.create_task(self._receive_loop())
        await self._listening.wait()

    async def disconnect(self):
        """ Disconnect from speaker. """
        if self._disconnecting:
            return
        self._disconnecting = True

        if self._event_writer:
            try:
                self._event_writer.close()
                await self._event_writer.wait_closed()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception('(%s) Unhandled exception when disconnecting', self._ip)

        self._event_reader = None
        self._event_writer = None

        self._disconnecting = False

    async def stop_listening(self):
        """ Stop listen to events from the speaker. """
        if self._listener_task:
            try:
                self._listener_task.cancel()
                await self._listener_task
            except asyncio.CancelledError:
                pass
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception('(%s) Unhandled exception when canceling listener task',
                                  self._ip)
            finally:
                self._listener_task = None
        self._listening.clear()

    async def request(self, api_call: ApiCall) -> ApiResponse:
        """ Send API to the speaker.

        Arguments:
            api_call:
                ApiCall object to send to the speaker.

        Returns:
            ApiResponse object with the requested information.

        Raises:
            ConnectionError: If not connected to the speaker.
            ApiCallTimeoutError: If correct response was not received.
        """
        if not self.is_connected or not self.is_listening:
            raise ConnectionError('No connection with speaker')

        # Make sure that a second call is not made until we receive a
        # correct answer or get time out on current call.
        while self._response_queue:
            await asyncio.sleep(1)

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
        except Exception as e:
            await self.disconnect()
            raise ConnectionError('Could not connect to speaker') from e

        # Send to the speaker.
        request = f'GET {api_call.url}{self._http_request}'
        writer.write(request.encode())
        await writer.drain()

        # For some API the speaker has no response.
        if not api_call.expected_response:
            return ApiResponse()

        # Wait for correct response.
        self._response_queue = asyncio.Queue(1)
        try:
            response = await asyncio.wait_for(
                self._wait_for_response(api_call),
                timeout=self._request_timeout * api_call.timeout_multiple)
        except asyncio.TimeoutError:
            raise ApiCallTimeoutError('No response from speaker')
        except Exception as e:
            raise ApiCallTimeoutError('Error while waiting for response') from e
        finally:
            # Reset writer and queue
            writer.close()
            await writer.wait_closed()
            self._response_queue = None

        return response

    async def _receive_loop_error(self) -> None:
        """ Cancel the receive loop task and disconnect. """
        await self.stop_listening()
        await self.disconnect()

    async def _receive_loop(self) -> None:
        """ Listen for api responses from the speaker.

        This method should be run as a asyncio task for receiving
        responses (events and api requests) from the speaker.
        """
        buffer: bytes = b''
        self._listening.set()
        try:
            while True:
                # If there is a problem with the StreamReader we need
                # to disconnect, so that the user can check this.
                if not self._event_reader:
                    break
                data = await self._event_reader.read(1024)
                # If we receive an empty byte something is wrong!
                if not data:
                    _LOGGER.warning('(%s) Disconnecting because listener received EOF', self._ip)
                    break
                _LOGGER.debug('(%s) Listener received data:', self._ip)
                _LOGGER.debug(data)
                data = buffer + data
                http_responses = parse_stream(data)
                for http_response in http_responses:
                    if http_response.body:
                        await self._response_handler(http_response)
                    buffer = http_response.remainder

        except asyncio.CancelledError:
            _LOGGER.debug('(%s) Receive loop is cancelled', self._ip)
            raise
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception('(%s) Disconnecting due to error while reading stream', self._ip)

        await self._receive_loop_error()

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
        except Exception as e:  # pylint: disable=broad-except
            api_response = api_error('ApiDecodingError', e, http_response.body)
            _LOGGER.warning('(%s) Error when decoding api response', self._ip)
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
            raise RuntimeError('asyncio.Queue not initialized')
        while True:
            api_response = await self._response_queue.get()
            if api_response.method != api_call.expected_response:
                continue
            if not api_call.user_check:
                return api_response
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
        for subscriber in self._subscribers:
            try:
                subscriber(api_response)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception('(%s) Error when trying to dispatch an event', self._ip)

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
            raise TypeError('Subscriber must be a callable')
        self._subscribers.add(callback)

    def unregister_subscriber(self, callback: Callable) -> None:
        """ Unregister listener.

        Arguments:
            callback:
                Callable to be removed from list of event subscribers.
        """
        self._subscribers.discard(callback)
