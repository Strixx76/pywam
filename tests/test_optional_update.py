"""Tests for unsupported optional speaker queries."""

"""Tests for unsupported optional speaker queries."""

import unittest
from unittest.mock import AsyncMock

from pywam.device import get_device_info
from pywam.lib.exceptions import ApiCallTimeoutError
from pywam.speaker import Speaker


class TestOptionalUpdate(unittest.IsolatedAsyncioTestCase):
    async def test_optional_timeout_is_remembered_for_dlna_source(self) -> None:
        speaker = Speaker("192.0.2.1")
        speaker.attribute._function = "wifi"
        speaker.attribute._submode = "dlna"

        async def request(call):
            if call.method in {"GetShuffleMode", "GetRepeatMode"}:
                raise ApiCallTimeoutError("unsupported query")

        speaker.client.request = AsyncMock(side_effect=request)

        await speaker.update_player_info()
        await speaker.update_player_info()

        methods = [call.args[0].method for call in speaker.client.request.call_args_list]
        self.assertEqual(methods.count("GetShuffleMode"), 1)
        self.assertEqual(methods.count("GetRepeatMode"), 1)
        self.assertEqual(methods.count("GetVolume"), 2)

    async def test_required_query_timeout_still_propagates(self) -> None:
        speaker = Speaker("192.0.2.1")
        speaker.client.request = AsyncMock(
            side_effect=ApiCallTimeoutError("required query failed")
        )

        with self.assertRaisesRegex(ApiCallTimeoutError, "required query failed"):
            await speaker.update_player_info()

    async def test_music_info_timeout_is_remembered_for_dlna_source(self) -> None:
        speaker = Speaker("192.0.2.1")
        speaker.attribute._function = "wifi"
        speaker.attribute._submode = "dlna"
        speaker.client.request = AsyncMock(
            side_effect=ApiCallTimeoutError("unsupported query")
        )

        await speaker.update_media_info()
        await speaker.update_media_info()

        methods = [call.args[0].method for call in speaker.client.request.call_args_list]
        self.assertEqual(methods.count("GetMusicInfo"), 1)

    def test_vl350_model_name_and_sources(self) -> None:
        info = get_device_info("WAH-VL350")

        self.assertEqual(info.name, "VL3")
        self.assertEqual(info.sources, ["Bluetooth", "Wi-Fi"])


if __name__ == "__main__":
    unittest.main()
