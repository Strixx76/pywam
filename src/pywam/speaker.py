# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Samsung Wireless Audio speaker (WAM). """
from __future__ import annotations

import asyncio
import functools
import logging
from typing import TYPE_CHECKING

from pywam.client import WamClient
from pywam.device import WamDevice, get_device_info
from pywam.events import WamEvents
from pywam.attributes import WamAttributes
from pywam.lib import api_call, validate
from pywam.lib.const import (
    APP_FEATURES,
    EXC_MESSAGE,
    Feature,
    SOURCES_BY_API,
    SOURCES_BY_NAME,
    SOURCE_FEATURES,
)
from pywam.lib.equalizer import EqualizerPreset
from pywam.lib.exceptions import ApiCallError, FeatureNotSupportedError, PywamError


if TYPE_CHECKING:
    from pywam.lib.api_response import ApiResponse
    from pywam.lib.media_presets import MediaPreset
    from pywam.lib.url import UrlMediaItem


_LOGGER = logging.getLogger(__name__)


def is_it_supported(func):
    """ Check if feature is supported in current state.

    We should always make sure that speaker support's the things
    we are to send to minimize the risk of "bricking" the device.

    Raises:
        FeatureNotSupportedError: If feature is not supported.
    """

    @functools.wraps(func)
    def wrapper_is_it_supported(self: Speaker, *args, **kwargs):
        if func.__name__ not in self.supported_features:
            raise FeatureNotSupportedError(
                f'({self.ip}) {EXC_MESSAGE[func.__name__]} is not supported in this mode.'
            )
        return func(self, *args, **kwargs)
    return wrapper_is_it_supported


class Speaker():
    """ Represents a Samsung Wireless Audio speaker (Samsung WAM).

    Arguments:
        ip:
            Speaker's IP address. (e.g "192.168.1.100")
        port (optional):
            TCP port that speaker listens on.
        user (optional):
            UUID for the connected user.
    """

    def __init__(self,
                 ip: str,
                 port: int = 55001,
                 user: str = '',
                 ) -> None:
        """ Initialize new speaker object. """
        self._ip: str = validate.ip(ip)
        self._port: int = validate.port(port)
        self._user: str = validate.user(user)
        self.device = WamDevice()
        self.attribute = WamAttributes(self, self.device)
        self.events = WamEvents(self)
        self.client = WamClient(self)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb) -> None:
        await self.disconnect()

    @property
    def ip(self) -> str:
        """ Return speaker ip address. """
        return self._ip

    @property
    def port(self) -> int:
        """ Return which TCP port speaker listens on. """
        return self._port

    @property
    def user(self) -> str:
        """ Return user id (UUID). """
        return self._user

    @property
    def supported_features(self) -> list[str]:
        """ Return a list of current supported features. """

        supported_features: list[str] = []

        # If speaker is slave in group only basic features are supported.
        if self.attribute.is_slave:
            return supported_features

        # Pause is supported by all services.
        # Select source is supported unless speaker is slave
        supported_features.extend([Feature.PAUSE, Feature.SELECT_SOURCE])

        # If we don't know all the needed attributes, we should return now.
        if self.attribute._grouptype is None or self.attribute._function is None:
            return supported_features

        # App and source dependant features
        if self.attribute.app_name:
            supported_features.extend(APP_FEATURES.get(self.attribute.app_name, []))
        if self.attribute.source:
            supported_features.extend(SOURCE_FEATURES.get(self.attribute.source, []))

        # If speaker is not grouped (master or slave) everything is supported
        if not self.attribute.is_master:
            supported_features.extend([Feature.SET_NAME])

        return supported_features

    # ******************************************************************
    # Connection
    # ******************************************************************
    async def connect(self,
                      connection_timeout: int = 5,
                      request_timeout: int = 5,
                      ) -> None:
        """ Connect to speaker.

        Arguments:
            connection_timeout (optional):
                Timeout in seconds for speaker connection.
            request_timeout (optional):
                Timeout when sending API commands to the speaker.

        Raises:
            ConnectionError: If no initial connection can be established.
        """
        self.client.request_timeout = request_timeout
        self.client.connection_timeout = connection_timeout
        self.client.register_subscriber(self.events.receiver)
        await self.client.connect()
        await self.client.start_listening()

    async def disconnect(self) -> None:
        """ Disconnect from speaker. """
        await self.client.stop_listening()
        await self.client.disconnect()
        self.client.unregister_subscriber(self.events.receiver)

    @property
    def is_connected(self) -> bool:
        """ Return True if connected to speaker, otherwise False. """
        if self.client.is_connected and self.client.is_listening:
            return True
        return False

    # ******************************************************************
    # Commands
    # ******************************************************************
    @is_it_supported
    async def cmd_next(self) -> None:
        """ Send next track command to speaker."""
        await self.client.request(api_call.set_trick_mode('next'))

    @is_it_supported
    async def cmd_pause(self) -> None:
        """ Send pause command to speaker. """
        if self.attribute._submode == 'dlna':
            await self.client.request(api_call.set_uic_playback_control('pause'))
        elif self.attribute._submode == 'cp':
            await self.client.request(api_call.set_cpm_playback_control('pause'))
        if self.attribute._submode == 'url' or self.attribute.app_name == 'Unknown':
            # For url_playback 'pause' is supported but not 'stop'.
            # But I have not found any way to resume it.
            # 'resume', 'play' and 'stop' is not supported for url_playback!
            # It has happened that it has resumed by it self hours after
            # it was paused. So until we find out how to resume it we
            # pause the stream and mute the speaker, and then set state
            # to stop.
            pause = await self.client.request(api_call.set_uic_playback_control('pause'))
            if pause.success:
                mute = await self.client.request(api_call.set_mute(True))
                if mute.success:
                    self.attribute._playstatus = 'stop'
                    self.attribute._cpname = 'Unknown'
                    self.attribute._submode = 'cp'

    @is_it_supported
    async def cmd_play(self) -> None:
        """ Send play command to speaker. """
        if self.attribute._submode == 'cp':
            await self.client.request(api_call.set_cpm_playback_control('play'))
        elif self.attribute._submode == 'dlna':
            await self.client.request(api_call.set_uic_playback_control('resume'))

    @is_it_supported
    async def cmd_previous(self) -> None:
        """ Send previous track command to speaker."""
        await self.client.request(api_call.set_trick_mode('previous'))

    @is_it_supported
    async def cmd_stop(self) -> None:
        """ Send stop command to speaker. """
        await self.client.request(api_call.set_cpm_playback_control('stop'))

    # ******************************************************************
    # Play
    # ******************************************************************
    @is_it_supported
    async def play_preset(self, preset: MediaPreset) -> None:
        """ Play TuneIn preset stored in speaker.

        Arguments:
            preset:
                MediaPreset object to play. Get available presets
                with :attr:`Speaker.attribute.media_presets`
        """
        try:
            preset = validate.media_preset(preset, self.attribute.tunein_presets)
        except ValueError as e:
            # If preset is not found on the speaker we update presets
            await self.client.request(api_call.set_select_radio())
            await self.client.request(api_call.get_preset_list(0, 30))
            raise e

        # At the moment only TuneIn presets are supported.
        if preset.app != 'TuneIn':
            raise FeatureNotSupportedError(f'({self.ip}) Only TuneIn presets supported')

        if preset.kind == 'speaker':
            preset_type = 1
        else:
            preset_type = 0
        preset_index = int(preset.contentid)

        result = await self.client.request(api_call.set_play_preset(preset_type, preset_index))
        if result.success and self.attribute.muted:
            await self.set_mute(False)

    @is_it_supported
    async def play_url(self, item: UrlMediaItem) -> None:
        """ Play from url.

        Plays a audio stream from an URL. Supported file formats:
        AAC (No DRM), MP3 (max 320kbps), OGG, WMA/WMV (1/2/3/7/9),
        WAV/FLAC/ALAC/AIFF (max 192kHz/24bit).
        NB! The speaker tries to play the body of the request no matter
        what it contains, and does no checking. If the file or body is
        not playable the speaker sometimes freezes, and you will have to
        unplug it to get it to respond again.
        The speaker sends no attributes when an url is played, so it is
        up to the user to set attributes using the UrlMediaItem.

        Arguments:
            item:
                UrlMediaItem with information about the url.
        """
        # Some speakers does't support the SetUrlPlayback API.
        # Maybe it depends on firmware version? We are not checking at
        # the moment.
        # https://sites.google.com/view/samsungwirelessaudiomultiroom/firmware

        item = validate.url_media_item(item)

        # Play url with 2Mb buffer size = 2097152
        result = await self.client.request(api_call.set_url_playback(item.url, 0, 0, 0))

        # *****************************************************
        # Workaround to set attributes not sent by the speaker.
        # *****************************************************
        if result.success:
            self.attribute._title = item.title
            self.attribute._description = item.description
            self.attribute._tracklength = item.duration
            self.attribute._thumbnail = item.thumbnail

        # We need to call all event subscribers after we have manually
        # set new attributes, otherwise the user will not be notified of
        # the change.
        self.events._dispatch_event(True, result)

        if result.success and self.attribute.muted:
            await self.set_mute(False)

    # ******************************************************************
    # Set
    # ******************************************************************
    async def set_mute(self, mute: bool) -> ApiResponse:
        """ Mute or unmute speaker.

        Arguments:
            mute:
                True for mute, False for unmute.

        Returns:
            MuteStatus
        """
        mute = validate.is_boolean(mute)
        return await self.client.request(api_call.set_mute(mute))

    @is_it_supported
    async def set_name(self, name: str) -> ApiResponse:
        """ Set speaker's name.

        Arguments:
            name:
                New speaker name.

        Returns:
            SpkName
        """
        name = validate.name(name)
        return await self.client.request(api_call.set_spk_name(name))

    @is_it_supported
    async def set_repeat_mode(self, repeat_mode: str) -> ApiResponse:
        """ Set repeat mode.

        Arguments:
            repeat_mode:
                One of the following modes: 'all', 'one' or 'off'.

        Returns:
            RepeatMode
        """
        if repeat_mode not in ['all', 'one', 'off']:
            raise ValueError(f'({self.ip}) Repeat mode not valid')
        return await self.client.request(api_call.set_uic_repeat_mode(repeat_mode))

    @is_it_supported
    async def set_shuffle(self, shuffle: bool) -> ApiResponse:
        """ Set shuffle mode.

        Arguments:
            shuffle:
                True for shuffle, False for continues mode.

        Returns:
            ShuffleMode
        """
        shuffle = validate.is_boolean(shuffle)
        return await self.client.request(api_call.set_shuffle_mode(shuffle))

    async def set_volume(self, volume: int) -> ApiResponse:
        """ Set volume level.

        Arguments:
            mute:
                Volume level (0-100).

        Returns:
            VolumeLevel
        """
        volume = validate.volume(volume)
        volume = self.device.encode_volume(volume)
        return await self.client.request(api_call.set_volume(volume))

    # ******************************************************************
    # Select
    # ******************************************************************
    @is_it_supported
    async def select_source(self, source: str) -> None:
        """ Select input source for speaker.

        Arguments:
            source:
                Name of source. One of the following, depending on
                speaker model: 'AUX', 'Bluetooth', 'Coaxial', 'HDMI',
                'HDMI 1', 'HDMI 2', 'Optical', 'TV SoundConnect',
                'USB' or 'Wi-Fi'.
                Available sources: :attr:`Speaker.attribute.source_list`
        """
        source = validate.source(source, self.attribute.source_list)
        source = SOURCES_BY_NAME[source]
        await self.client.request(api_call.set_func(source))

    async def select_sound_mode(self, preset: EqualizerPreset) -> None:
        """ Select sound mode for speaker.

        Arguments:
            preset:
                EqualizerPreset to use. Get available presets with
                :attr:`Speaker.attribute.sound_mode_list`
        """
        preset = validate.equalizer_preset(preset, self.attribute.sound_mode_list)
        await self.client.request(api_call.set_7band_eq_mode(preset.index))

    # ******************************************************************
    # Update
    # ******************************************************************

    async def update(self) -> None:
        """ Update all speaker properties.

        This method should be called after a connection to the speaker
        is established. After that there is normally no need for calling
        this any more, since the state is updated as long as the
        connection to speaker remains.
        """
        # NB! It must be in this order!
        await self.update_speaker_info()
        await self.update_player_info()
        await self.update_media_info()
        await self.update_speaker_settings()

        # Store speaker model specifics
        self.device.update_model(self.attribute._spkmodelname)

    async def update_speaker_info(self) -> None:
        """ Update speaker info. """
        # Main speaker info
        await self.client.request(api_call.get_main_info())
        # Names
        await self.client.request(api_call.get_spk_name())
        if self.attribute._grouptype != 'N':
            await self.client.request(api_call.get_group_name())
        # Firmware version
        await self.client.request(api_call.get_software_version())
        # Network connection
        await self.client.request(api_call.get_ap_info())
        # Connected clients
        # TODO: Get 'IpInfo' - Don't know the API-call to make.

    async def update_player_info(self) -> None:
        """ Update player attributes. """
        await self.client.request(api_call.get_func())
        await self.client.request(api_call.get_volume())
        await self.client.request(api_call.get_mute())
        await self.client.request(api_call.get_shuffle_mode())
        await self.client.request(api_call.get_repeat_mode())
        await self.client.request(api_call.get_current_eq_mode())

    async def update_media_info(self) -> None:
        """ Update current media attributes. """
        if self.attribute._function == 'wifi' and self.attribute._submode == 'cp':
            await self.client.request(api_call.get_radio_info())
        elif self.attribute._function == 'wifi' and self.attribute._submode == 'dlna':
            await self.client.request(api_call.get_music_info())

    async def update_speaker_settings(self) -> None:
        """ Update speaker settings. """
        # Favorites. At the moment only TuneIn presets are supported.
        await self.client.request(api_call.set_select_radio())
        await self.client.request(api_call.get_preset_list(0, 30))
        # Equalizer
        await self.client.request(api_call.get_7band_eq_list())

    # ******************************************************************
    # Get
    # ******************************************************************

    async def get_model(self) -> str:
        """ Get model name of speaker.

        Returns:
            Model name of speaker.

        Raise:
            ApiCallError if call failed.
        """
        response = await self.client.request(api_call.get_main_info())
        if model := response.get_key('spkmodelname'):
            device = get_device_info(model)
            return device.name
        raise ApiCallError(f'({self.ip}) API call failed')

    async def get_mute(self) -> bool:
        """ Get mute state of speaker.

        Returns:
            True if speaker is muted.

        Raise:
            ApiCallError if call failed.
        """
        response = await self.client.request(api_call.get_mute())
        if mute := response.get_key('mute'):
            return (mute == 'on')
        raise ApiCallError(f'({self.ip}) API call failed')

    async def get_name(self) -> str:
        """ Get speaker's name.

        Returns:
            Speaker name.

        Raise:
            ApiCallError if call failed.
        """
        response = await self.client.request(api_call.get_spk_name())
        if name := response.get_key('spkname'):
            return name
        raise ApiCallError(f'({self.ip}) API call failed')

    async def get_source(self) -> str:
        """ Get current selected source on speaker.

        Returns:
            Name of current selected source.

        Raise:
            ApiCallError if call failed.
        """
        response = await self.client.request(api_call.get_func())
        if source := response.get_key('function'):
            return SOURCES_BY_API.get(source, 'Unknown')
        raise ApiCallError(f'({self.ip}) API call failed')

    async def get_speaker_id(self) -> str:
        """ Get speaker ID.

        Returns:
            ID of speaker.

        Raise:
            ApiCallError if call failed.
        """
        response = await self.client.request(api_call.get_device_id())
        if speaker_id := response.get_key('device_id'):
            return speaker_id
        raise ApiCallError(f'({self.ip}) API call failed')

    async def get_tunein_presets(self) -> list[dict[str, str]]:
        """ Get TuneIn presets stored in speaker.

        Returns:
            List of TuneIn presets.

        Raise:
            ApiCallError if call failed.
        """
        await self.client.request(api_call.set_select_radio())
        response = await self.client.request(api_call.get_preset_list(0, 30))
        if response.get_key('cpname') == 'tunein':
            return response.get_subkey('presetlist', 'preset')
        else:
            raise ApiCallError(f'({self.ip}) API call failed')

    async def get_volume(self) -> int:
        """ Get volume level.

        Returns:
            Speaker volume (0-100).

        Raise:
            ApiCallError if call failed.
        """
        response = await self.client.request(api_call.get_volume())
        if volume := response.get_key('volume'):
            return self.device.decode_volume(int(volume))
        raise ApiCallError(f'({self.ip}) API call failed')

    # *********************************************************************************************
    # Group
    # *********************************************************************************************

    async def group(self,
                    slaves_before: list[Speaker],
                    slaves_after: list[Speaker],
                    group_name: str | None = None
                    ) -> None:
        """ Group this speaker.

        Create or edit a speaker groupe. This method can only be called
        when the speaker is already master in the the groupe or if it is
        not in a group.
        If the speaker is already master you must provide all the slaves
        because the speaker is not aware of its slaves.

        Arguments:
            slaves_before:
                List of all the slaves in the group, or empty list if
                the speaker is not yet master.
            slaves_after:
                List of all the slaves in the group, or empty list if
                the group should be deleted.
        """
        # Check that we have needed attributes to call grouping API
        if (
            self.attribute.mac is None or
            self.attribute.name is None or
            self.attribute.is_grouped is None
        ):
            raise PywamError(f'({self.ip}) Speaker attributes not available')

        # If this speaker is slave to another group it can't be master
        # in a new group.
        if self.attribute.is_slave:
            raise PywamError(f'({self.ip}) This speaker is already a slave in another group')

        # Validate all slave speakers
        slaves_before = validate.speakers(slaves_before)
        slaves_after = validate.speakers(slaves_after)

        speakers_to_add = list(set(slaves_after)-set(slaves_before))
        speakers_to_remove = list(set(slaves_before)-set(slaves_after))

        if not self.attribute.is_grouped and len(slaves_before) > 0:
            raise PywamError(f'({self.ip}) Speaker has no slaves now')

        for speaker in slaves_before:
            if speaker.attribute.master_ip != self.ip:
                raise PywamError(f'"{speaker.ip}" is not a slave in this group')

        for speaker in speakers_to_add:
            if speaker.attribute.is_grouped:
                raise PywamError(f'"{speaker.ip}" is already grouped')

        subspeakers = []
        for speaker in slaves_after:
            if speaker.attribute.mac is None:
                raise PywamError(f'"{speaker.ip}" has no MAC')
            else:
                subspeakers.append({'ip': speaker.ip, 'mac': speaker.attribute.mac})

        # Set group name
        if not group_name:
            group_name = f'{self.attribute.name}_group'
        group_name = validate.name(group_name)

        # Remove speakers
        api_calls = []
        for speaker in speakers_to_remove:
            _LOGGER.info('(%s) Adding "%s" to be removed', self.ip, speaker.attribute.name)
            api_calls.append(speaker.client.request(api_call.set_ungroup()))
        _LOGGER.info('(%s) Removing %s speakers from group', self.ip, len(api_calls))
        await asyncio.gather(*api_calls)

        # Delete group if no slaves after
        if len(slaves_after) == 0:
            _LOGGER.info('(%s) Deleting group by send ungroup to master', self.ip)
            await self.client.request(api_call.set_ungroup())
            return

        # Update group
        api = api_call.set_multispk_group_mainspk(
            group_name,
            len(subspeakers) + 1,
            self.attribute.mac,
            self.attribute.name,
            subspeakers,
        )
        _LOGGER.info('(%s) Calling master with updated group info', self.ip)
        _LOGGER.info(' - Subspeakers: %s', subspeakers)
        _LOGGER.info(' - Groupname: %s', group_name)
        await self.client.request(api)

        # Call added slaves
        api_calls = []
        for speaker in slaves_after:
            api = api_call.set_multispk_group_subspk(
                group_name,
                len(subspeakers) + 1,
                self.ip,
                self.attribute.mac,
            )
            _LOGGER.info('(%s) %s will soon be called and set to slave',
                         self.ip, speaker.attribute.name)
            api_calls.append(speaker.client.request(api))
        _LOGGER.info('(%s) Calling all slaves with updated information', self.ip)
        await asyncio.gather(*api_calls)
