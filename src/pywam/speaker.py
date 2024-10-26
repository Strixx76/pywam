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
from pywam.events import WamEvents
from pywam.attributes import WamAttributes
from pywam.lib import api_call, translate, validate
from pywam.lib.const import APP_FEATURES, EXC_MESSAGE, Feature, SOURCE_FEATURES
from pywam.lib.equalizer import EqualizerPreset
from pywam.lib.exceptions import ApiCallError, FeatureNotSupportedError


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
    def wrapper_is_it_supported(self, *args, **kwargs):
        if func.__name__ not in self.supported_features:
            raise FeatureNotSupportedError(f'{EXC_MESSAGE[func.__name__]} is not supported in this mode.')
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
        self.attribute = WamAttributes(self)
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
        supported_features.extend([Feature.PAUSE])

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
            supported_features.extend([Feature.SELECT_SOURCE, Feature.SET_NAME])

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
        if self.attribute._submode == 'cp':
            await self.client.request(api_call.set_cpm_playback_control('pause'))
        elif self.attribute._submode == 'dlna':
            await self.client.request(api_call.set_uic_playback_control('pause'))
        elif self.attribute._submode == 'url' or self.attribute._submode == 'Unknown':
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
            raise FeatureNotSupportedError('Only TuneIn presets supported')

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
            raise ValueError('Repeat mode not valid')
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
        volume = translate.encode_volume(volume)
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
                speaker model: 'AUX', 'Bluetooth', 'HDMI', 'HDMI 1',
                'HDMI 2', 'Optical', 'TV SoundConnect', 'Wi-Fi', 'USB'.
                Available sources: :attr:`Speaker.attribute.source_list`
        """
        source = validate.source(source, self.attribute._spkmodelname)
        source = translate.encode_source(source)
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
        if not translate._init:
            translate.init(self.attribute._spkmodelname)

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
            return translate.model(model)
        raise ApiCallError

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
        raise ApiCallError

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
        raise ApiCallError

    async def get_source(self) -> str:
        """ Get current selected source on speaker.

        Returns:
            Name of current selected source.

        Raise:
            ApiCallError if call failed.
        """
        response = await self.client.request(api_call.get_func())
        if source := response.get_key('function'):
            return translate.decode_source(source)
        raise ApiCallError

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
        raise ApiCallError

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
            raise ApiCallError

    async def get_volume(self) -> int:
        """ Get volume level.

        Returns:
            Speaker volume (0-100).

        Raise:
            ApiCallError if call failed.
        """
        response = await self.client.request(api_call.get_volume())
        if volume := response.get_key('volume'):
            return translate.decode_volume(int(volume))
        raise ApiCallError

    # *********************************************************************************************
    # Group
    # *********************************************************************************************
    async def create_group(self, slaves: list[Speaker], group_name: str | None = None) -> None:
        """ Create a speaker group.

        This speaker will become the master speaker of the group, and
        passed in list of speakers will become slaves.
        The speakers can't already be part of another group.
        It is up to the user to keep track of groups and group members.
        The master knows nothing about it's slaves, only how many.

        Arguments:
            slaves:
                A list of Speaker objects to group with this speaker.
            group_name (opt):
                Name of the group. If not given the groups will named as
                master speaker with suffix '_group'.

        Raises:
            FeatureNotSupportedError if the speaker belongs to another group.
        """

        # If this speaker is slave to another group it can't be master
        # in a new group.
        if self.attribute.is_slave:
            raise FeatureNotSupportedError('This speaker is already a slave in another group')

        # Set group name
        if not group_name:
            group_name = f'{self.attribute.name}_group'
        group_name = validate.name(group_name)

        # Validate all slave speakers
        slaves = validate.speakers(slaves)
        subspeakers = []
        for speaker in slaves:
            # If a speakers already belongs to another grouped we can't
            # add it to this group
            if speaker.attribute.is_grouped:
                if speaker.attribute.master_ip != self.ip:
                    _LOGGER.error("(%s) Speaker already belongs to another group", speaker.ip)
                    continue
                if speaker.attribute.is_master:
                    _LOGGER.error("(%s) Speaker already master in another group", speaker.ip)
                    continue
            subspeakers.append({'ip': speaker.ip, 'mac': speaker.attribute.mac})
        if len(subspeakers) == 0:
            raise FeatureNotSupportedError('No speakers to be group')

        api = api_call.set_multispk_group_mainspk(
            group_name,
            len(subspeakers) + 1,
            self.attribute.mac,
            self.attribute.name,
            subspeakers,
        )
        await self.client.request(api)

        api_calls = []
        for speaker in slaves:
            api = api_call.set_multispk_group_subspk(
                group_name,
                len(subspeakers) + 1,
                self.ip,
                self.attribute.mac,
            )
            api_calls.append(speaker.client.request(api))
        await asyncio.gather(*api_calls)

    async def delete_group(self, slaves: list[Speaker]) -> None:
        """ Delete a speaker group.

        Removes this and all slave speaker from the group. All slaves
        in the group must be passed.
        There is no way for the master to know which speakers that
        belong to this group. It is up to the user to keep track of this.

        Arguments:
            slaves:
                A list of Speaker objects in current group.
            group_name (opt):
                Name of the group. If not given the groups will named as
                master speaker with suffix '_group'.

        Raises:
            FeatureNotSupportedError if the speaker is not a master.
        """
        if not self.attribute.is_master:
            raise FeatureNotSupportedError('This speaker is not master in any group')

        slaves = validate.speakers(slaves)

        api_calls = []
        for speaker in slaves:
            if speaker.attribute.master_ip != self.ip:
                _LOGGER.error("(%s) is not a slave to this speaker.", speaker.ip)
                continue
            api_calls.append(speaker.client.request(api_call.set_ungroup()))

        await asyncio.gather(*api_calls)
        await self.client.request(api_call.set_ungroup())

    async def leave_group(self, master: Speaker, slaves: list[Speaker] = []) -> None:
        """ Leave a speaker group.

        When the speaker is part of a group you call this to leave that
        group. This can only be called if the speaker is a slave.

        Arguments:
            master:
                Speaker object for the master of the group.
            slaves:
                A list of Speaker objects for all the other slaves in
                the group to leave.
                None if there are no other speakers in the group.
        """
        if not self.attribute.is_slave:
            raise FeatureNotSupportedError('This speaker is not slave in any group')

        master = validate.speakers([master])[0]

        if self.attribute.master_ip != master.ip:
            raise FeatureNotSupportedError('Given master speaker is not the master in this group')

        await self.client.request(api_call.set_ungroup())

        if slaves:
            slaves = validate.speakers(slaves)
            await master.create_group(slaves, master.attribute.group_name)
        else:
            await master.client.request(api_call.set_ungroup())
