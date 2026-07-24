"""Regression tests for the `fix/tolerate-unanswered-update-calls` branch.

`update_player_info()` / `update_speaker_settings()` must tolerate the
speaker ignoring optional queries (shuffle/repeat/presets) that are
meaningless for the active source, caching the skip keyed by source so a
source change retries it. Each test PASSES on this branch and FAILS on
`master` (via the ``PYWAM_SRC`` env var in ``conftest.py``).

There is no real speaker; the network client / socket layer is mocked.
"""
from __future__ import annotations

import pytest

from pywam.lib import api_call
from pywam.lib.api_response import ApiResponse
from pywam.lib.exceptions import ApiCallTimeoutError
from pywam.speaker import Speaker

TEST_IP = "192.168.1.100"


def _ok(method: str = "", data=None) -> ApiResponse:
    """Build a benign, successful ApiResponse."""
    if data is None:
        data = {"@result": "ok"}
    return ApiResponse(method=method, success=True, data=data)


# ======================================================================
# Fix: update() tolerates source-unsupported calls, keyed by source
# ======================================================================


class _RecordingClient:
    """Stand-in for WamClient.request that records calls and can time out.

    Methods listed in ``timeout_methods`` raise ApiCallTimeoutError (as a
    real speaker does when the query is meaningless for the active
    source, e.g. shuffle/repeat/presets on an HDMI input); every other
    call returns a benign successful response.
    """

    def __init__(self, timeout_methods: set[str]) -> None:
        self.timeout_methods = timeout_methods
        self.calls: list[str] = []

    async def request(self, call: api_call.ApiCall) -> ApiResponse:
        self.calls.append(call.method)
        if call.method in self.timeout_methods:
            raise ApiCallTimeoutError(f"({TEST_IP}) No response from speaker")
        return _ok(call.expected_response)


@pytest.mark.asyncio
async def test_update_player_info_tolerates_unanswered_calls_per_source():
    """update_player_info() must not abort when the speaker ignores the
    optional shuffle/repeat queries (HDMI source), and must cache the
    skip keyed by source so a source change retries it."""
    speaker = Speaker(TEST_IP)
    fake = _RecordingClient(timeout_methods={"GetShuffleMode", "GetRepeatMode"})
    speaker.client.request = fake.request  # type: ignore[assignment]

    # Active source is an external HDMI input.
    speaker.attribute._function = "hdmi"

    # On this branch this completes; on master the raw request() for
    # GetShuffleMode raises ApiCallTimeoutError straight out.
    await speaker.update_player_info()

    # The unanswered optional calls were cached, keyed by the source.
    assert ("hdmi", "GetShuffleMode") in speaker._unsupported
    assert ("hdmi", "GetRepeatMode") in speaker._unsupported

    # A second pass in the SAME source skips them (request not re-issued).
    calls_before = fake.calls.count("GetShuffleMode")
    await speaker.update_player_info()
    assert fake.calls.count("GetShuffleMode") == calls_before

    # Changing the source re-enables the query (per-source, not permanent).
    speaker.attribute._function = "wifi"
    await speaker.update_player_info()
    assert fake.calls.count("GetShuffleMode") == calls_before + 1


@pytest.mark.asyncio
async def test_update_speaker_settings_tolerates_unanswered_preset_call():
    """update_speaker_settings() must tolerate the speaker ignoring the
    preset-list query in a non-radio source."""
    speaker = Speaker(TEST_IP)
    fake = _RecordingClient(timeout_methods={"GetPresetList"})
    speaker.client.request = fake.request  # type: ignore[assignment]

    speaker.attribute._function = "hdmi"

    # Completes on this branch; raises ApiCallTimeoutError on master.
    await speaker.update_speaker_settings()

    assert ("hdmi", "GetPresetList") in speaker._unsupported
