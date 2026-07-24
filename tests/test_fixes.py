"""Regression test for the `fix/listener-deadlock` branch.

`_return_response()` must not block the listener when the response queue
is already at capacity (trailing-message case). The test PASSES on this
branch and FAILS on `master` (via the ``PYWAM_SRC`` env var in
``conftest.py``).

There is no real speaker; the network client / socket layer is mocked.
"""
from __future__ import annotations

import asyncio

import pytest

from pywam.lib.api_response import ApiResponse
from pywam.speaker import Speaker

TEST_IP = "192.168.1.100"


def _ok(method: str = "", data=None) -> ApiResponse:
    """Build a benign, successful ApiResponse."""
    if data is None:
        data = {"@result": "ok"}
    return ApiResponse(method=method, success=True, data=data)


# ======================================================================
# Fix: listener does not deadlock on a full response queue
# ======================================================================


@pytest.mark.asyncio
async def test_return_response_does_not_block_on_full_queue():
    """_return_response() must not block the listener when the response
    queue is already at capacity (trailing message case)."""
    speaker = Speaker(TEST_IP)
    client = speaker.client

    # Pre-fill the single-slot queue to capacity.
    client._response_queue = asyncio.Queue(1)
    client._response_queue.put_nowait(_ok("MuteStatus"))

    trailing = _ok("MuteStatus")

    # On this branch put_nowait -> QueueFull is caught and the message is
    # dropped, so this returns immediately. On master `await queue.put()`
    # blocks forever on the full queue, so wait_for raises TimeoutError.
    await asyncio.wait_for(client._return_response(trailing), timeout=1.0)

    # The original item is still there (trailing message was dropped).
    assert client._response_queue.qsize() == 1
