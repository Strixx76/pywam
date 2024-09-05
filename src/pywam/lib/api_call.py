# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Samsung WAM API object factory.

All wrapper functions returns a :class:`ApiCall` to be used when calling
:meth:`pywam.client.WamClient.request`.
All known responses to the different API calls are documented in
:module:`pywam.events`.
"""

from __future__ import annotations

import urllib.parse


class ApiCall:
    """ API message to speaker.

    Arguments:
        api_type:
            Type of API call, 'UIC' or 'CPM'.
        method:
            API method name.
        args (optional):
            List of tuples with arguments for the api method.
            First item: Name of the argument.
            Second item: Value of argument.
            Third item: Type hint. ('str'|'dec'|'cdata'|'dec_arr')
        expected_response (optional):
            Expected name of method in response.
        user_check (optional):
            True if response should be checked against user ID of sender.
        timeout_multiple (optional):
            Multiples of API timeout.
    """
    __slots__ = ('api_type', 'method', 'args', 'pwron', 'expected_response',
                 'user_check', 'timeout_multiple')

    # pylint: disable=dangerous-default-value
    def __init__(self,
                 api_type: str,
                 method: str,
                 pwron: bool = False,
                 args: list[tuple[str, str | int | list[int], str]] = [],
                 expected_response: str = '',
                 user_check: bool = False,
                 timeout_multiple: int = 1,
                 ) -> None:
        """ Create a ApiCall object. """
        self.api_type = api_type
        self.method = method
        self.pwron = pwron
        self.args = args
        self.expected_response = expected_response
        self.user_check = user_check
        self.timeout_multiple = timeout_multiple

    def __str__(self):
        return ('ApiCall:\n' +
                f'api_type: {self.api_type}\n' +
                f'method: {self.method}\n' +
                f'pwron: {self.pwron}\n' +
                f'args: {self.args}\n' +
                f'expected_response: {self.expected_response}\n' +
                f'user_check: {self.user_check}\n' +
                f'timeout_multiple: {self.timeout_multiple}\n'
                )

    @property
    def url(self) -> str:
        """ ASCII encoded URL safe string with API call. """
        # pwron
        if self.pwron:
            payload = ['<pwron>on</pwron>']
        else:
            payload = []

        # method
        payload.append(f'<name>{self.method}</name>')

        # arguments
        if self.args:
            for arg in self.args:
                name, value, type_hint = arg
                if type_hint == 'cdata':
                    payload.append(f'<p type="{type_hint}" name="{name}" val="empty">'
                                   f'<![CDATA[{value}]]></p>')
                elif type_hint == 'str_arr' or type_hint == 'dec_arr':
                    if isinstance(value, list):
                        value = ''.join([f'<item>{v}</item>' for v in value])
                    else:
                        value = f'<item>{value}</item>'
                    payload.append(f'<p type="{type_hint}" name="{name}" val="empty">'
                                   f'{value}</p>')
                else:
                    payload.append(f'<p type="{type_hint}" name="{name}" val="{value}"/>')

        # create url
        cmd = ''.join(payload)
        return f'/{self.api_type}?cmd={urllib.parse.quote(cmd)}'


# **********************************************************************
# Speaker info
# **********************************************************************

def get_software_version() -> ApiCall:
    """ (UIC) Get software version on speaker. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetSoftwareVersion',
                   args=[],
                   expected_response='SoftwareVersion',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_spk_name() -> ApiCall:
    """ (UIC) Get speaker name. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetSpkName',
                   args=[],
                   expected_response='SpkName',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_spk_name(spkname: str) -> ApiCall:
    """ (UIC) Set speaker name.

    Arguments:
        spkname:
            New speaker name.
    """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='SetSpkName',
                   args=[('spkname', spkname, 'cdata')],
                   expected_response='SpkName',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_main_info() -> ApiCall:
    """ (UIC) Get main information about speaker.

    Important:
        Api call will cause the following events/responses:
            'RequestDeviceInfo':
                Empty response without any information.
            'MainInfo':
                The response with information about the speaker.
    """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetMainInfo',
                   args=[],
                   expected_response='MainInfo',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_device_id() -> ApiCall:
    """ (CPM) Get speaker ID. """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='GetDeviceId',
                   args=[],
                   expected_response='DeviceId',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_ap_info() -> ApiCall:
    """ (UIC) Get information about network connection. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetApInfo',
                   args=[],
                   expected_response='ApInfo',
                   user_check=False,
                   timeout_multiple=1,
                   )


# **********************************************************************
# Player and media
# **********************************************************************

def get_volume() -> ApiCall:
    """ (UIC) Get current volume level. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetVolume',
                   args=[],
                   expected_response='VolumeLevel',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_volume(volume: int) -> ApiCall:
    """ (UIC) Set speaker volume level.

    Arguments:
        volume:
            Volume level between 0 and 30.
    """
    return ApiCall(api_type='UIC',
                   pwron=True,
                   method='SetVolume',
                   args=[('volume', volume, 'dec')],
                   expected_response='VolumeLevel',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_mute() -> ApiCall:
    """ (UIC) Get mute state of the speaker. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetMute',
                   args=[],
                   expected_response='MuteStatus',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_mute(mute: bool) -> ApiCall:
    """ (UIC) Set mute/unmute state of the speaker.

    Arguments:
         mute:
            True to mute.
    """
    return ApiCall(api_type='UIC',
                   pwron=True,
                   method='SetMute',
                   args=[('mute', 'on' if mute else 'off', 'str')],
                   expected_response='MuteStatus',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_shuffle_mode() -> ApiCall:
    """ (UIC) Retrieve currently set shuffle mode. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetShuffleMode',
                   args=[],
                   expected_response='ShuffleMode',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_shuffle_mode(shuffle_mode: bool) -> ApiCall:
    """ (UIC) Enable/disable shuffle mode of the playlist.

    Arguments:
        shuffle_mode:
            True for shuffle mode
    """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='SetShuffleMode',
                   args=[('shufflemode', 'on' if shuffle_mode else 'off', 'str')],
                   expected_response='ShuffleMode',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_repeat_mode() -> ApiCall:
    """ (UIC) Get playback repeat mode. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetRepeatMode',
                   args=[],
                   expected_response='RepeatMode',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_uic_repeat_mode(repeat_mode: str) -> ApiCall:
    """ (UIC) Set playback repeat mode.

    Arguments:
        mode:
            Repeat mode. ('one' | 'all' | 'off')
    """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='SetRepeatMode',
                   args=[('repeatmode', repeat_mode, 'str')],
                   expected_response='RepeatMode',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_cp_info() -> ApiCall:
    """ (CPM) Get info about currently selected cp service.

    This does not mean that the speaker is playing this cp at the
    moment, only that this is the cp selected for doing operations
    on. E.g: if you want to get TuneIn presets from the speaker but
    the current selected cp is Spotify, you will try to get presets
    from Spotify, which is not supported.
    """
    # TODO: This API can have arguments, but I don't know what and why
    # <p type="str" name="cpname" val="%s"/>
    # <p type="str" name="cpname" val="Spotify"/>
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='GetCpInfo',
                   args=[],
                   expected_response='CpInfo',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_func(func: str) -> ApiCall:
    """ (UIC) Set the source for the speaker.

    Arguments:
        source:
            Source to select.
            ('aux' | 'bt' | 'hdmi' | 'optical' | 'soundshare' | 'wifi')
    """
    return ApiCall(api_type='UIC',
                   pwron=True,
                   method='SetFunc',
                   args=[('function', func, 'str')],
                   expected_response='CurrentFunc',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_func() -> ApiCall:
    """ (UIC) Get current source for the speaker. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetFunc',
                   args=[],
                   expected_response='CurrentFunc',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_uic_playback_control(command: str) -> ApiCall:
    """ (UIC) Pause/resume current playlist.

    This is for UIC services (DLNA, USB...).

    Arguments:
        command:
            'resume' | 'pause'

    Important:
        Api call will cause the following events/responses:
            'PlaybackStatus':
                Confirmation that call is received by speaker.
            'PausePlaybackEvent':
                When playback is paused. Can be received before
                'PlaybackStatus'
            'StartPlaybackEvent':
                When playback is resumed. Can be received before
                'PlaybackStatus'
    """
    return ApiCall(api_type='UIC',
                   pwron=True,
                   method='SetPlaybackControl',
                   args=[('playbackcontrol', command, 'str')],
                   expected_response='PlaybackStatus',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_cpm_playback_control(command: str) -> ApiCall:
    """ (CPM) Play/pause/stop current selected cp.

    This is for CPM apps. (TuneIn, Spotify, Amazon...)
    Not all commands work on all cp.
    TuneIn: play | pause | stop
    Spotify: play | pause

    Arguments:
        command:
            'play' | 'pause' | 'stop'

    Important:
        Api call will cause the following events/responses:
            'PlaybackStatus':
                Confirmation that call is received by speaker.
            'PausePlaybackEvent':
                When playback is paused. Can be received before
                'PlaybackStatus'
            'StartPlaybackEvent':
                When playback is resumed. Can be received before
                'PlaybackStatus'
    """
    return ApiCall(api_type='CPM',
                   pwron=True,
                   method='SetPlaybackControl',
                   args=[('playbackcontrol', command, 'str')],
                   expected_response='PlaybackStatus',
                   user_check=False,
                   timeout_multiple=5,
                   )


def set_trick_mode(trick_mode: str) -> ApiCall:
    """ (UIC) Move to next/previous track on the playlist.

    Arguments:
        trick_mode:
            'next' | 'previous'
    """
    return ApiCall(api_type='UIC',
                   pwron=True,
                   method='SetTrickMode',
                   args=[('trickmode', trick_mode, 'str')],
                   # TODO: Expected response
                   expected_response='',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_radio_info() -> ApiCall:
    """ (CPM) Get information about what is playing.

    This is for CPM apps. (TuneIn, Spotify, Amazon...). Function must be
    'wifi' and submode 'cp'.

    Important:
        For UIC services (DLNA, USB...) you should use
        :func:`get_music_info`
    """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='GetRadioInfo',
                   args=[],
                   expected_response='RadioInfo',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_music_info() -> ApiCall:
    """ (UIC) Get information about what is playing.

    This is for UIC services (DLNA, USB...). If function is 'wifi
    submode must be 'dlna'.

    Important:
        For CPM apps (TuneIn, Spotify, Amazon... ) you should use
        :func:`get_radio_info`
    """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetMusicInfo',
                   args=[],
                   expected_response='MusicInfo',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_url_playback(url: str, buffersize: int, seektime: int, resume: int) -> ApiCall:
    """ (UIC) Play from url.

    Plays a audio file or stream from an URL. Supported file
    formats: AAC (No DRM), MP3 (max 320kbps), OGG,
    WMA/WMV (1/2/3/7/9), WAV/FLAC/ALAC/AIFF (max 192kHz/24bit).
    NB! The speaker tries to play the response body from the request
    no matter what it contains, and does no checking. If the body
    does not contain a playable bytes object the speaker will
    freeze, and you will have to unplug it to get it to respond
    again.

    Arguments:
        url:
            URL to play
        buffersize:
            Buffer size in bytes. strangely playback seems more stable
            when you set buffer to 0. But needs more testing.
        seektime:
            ???
        resume:
            0 = Do not resume previous service
            1 = resume Does not work for TuneIn or Spotify
    """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='SetUrlPlayback',
                   args=[('url', url, 'cdata'),
                         ('buffersize', int(buffersize), 'dec'),
                         ('seektime', int(seektime), 'dec'),
                         ('resume', int(resume), 'dec'), ],
                   expected_response='UrlPlayback',
                   user_check=False,
                   timeout_multiple=5,
                   )


# **********************************************************************
# Favorites
# **********************************************************************

def set_select_radio() -> ApiCall:
    """ (CPM) Select radio.

    Must be selected before sending commands for TuneIn. If you have
    another cp selected get_preset_list will respond with an error.
    Some commands will work, but there will be unwanted side
    effects. For example if you have Spotify selected and playing and
    call to start playing a radio channel, the channel will play, but
    Spotify will not know that you have change service.
    """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='SetSelectRadio',
                   args=[],
                   expected_response='RadioSelected',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_preset_list(start_index: int, list_count: int) -> ApiCall:
    """ (CPM) Get presets stored in speaker.

    Will return an error (- errcode: 73) if not radio is selected.

    Arguments:
        startindex:
            Starting position to retrieve
        listcount:
            Total number of items to retrieve
    """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='GetPresetList',
                   args=[('startindex', start_index, 'dec'),
                         ('listcount', list_count, 'dec'),
                         ],
                   expected_response='PresetList',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_play_preset(preset_type: int,
                    preset_index: int) -> ApiCall:
    """ (CPM) Select preset of a particular index.

    Arguments:
        preset_type:
            1 - speaker, 0 - my
        preset_index:
            Index of get preset list

    Important:
        Api call will cause the following events/responses:
            'RadioInfo':
                Confirmation that call is received by speaker.
            'MediaBufferStartEvent':
                When starting buffering the selected preset.
            'MediaBufferEndEvent':
                When ready buffering.
            'StartPlaybackEvent':
                When actually starting to play selected preset.
    """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='SetPlayPreset',
                   args=[('presettype', int(preset_type), 'dec'),
                         ('presetindex', int(preset_index), 'dec'), ],
                   expected_response='RadioInfo',
                   user_check=False,
                   timeout_multiple=5,
                   )


# **********************************************************************
# Grouping
# **********************************************************************

def get_group_name() -> ApiCall:
    """ (UIC) Get name of speaker group. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetGroupName',
                   args=[],
                   expected_response='GroupName',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_multispk_group_mainspk(name: str,
                               spknum: int,
                               audiosourcemacaddr: str,
                               audiosourcename: str,
                               subspeakers: list[dict[str, str]]
                               ) -> ApiCall:
    """ (UIC) Group speakers.

    This API call should be sent to the master speaker in a group.

    Arguments:
        name:
            Group name.
        spknum:
            Number of speakers in the group.
        audiosourcemacaddr:
            Master speaker MAC address.
        audiosourcename:
            Name of master.
        subspeakers:
            A list of dictionaries containing slave speakers ip and mac address.
            {'ip': ipaddress, 'mac': mac address}

    Notes:
        Following API-attributes does not seem to change and is therefore not
        arguments to this ApiCall factory.

        index:
            "1" always works
        type:
            "main" because this is for the master speaker.
        audiosourcetype:
            Should be "speaker". Have not found any information about
            optional values.
    """
    args = [('name', name, 'cdata'),
            ('index', 1, 'dec'),
            ('type', 'main', 'str'),
            ('spknum', spknum, 'dec'),
            ('audiosourcemacaddr', audiosourcemacaddr, 'str'),
            ('audiosourcename', audiosourcename, 'cdata'),
            ('audiosourcetype', 'speaker', 'str'),
            ]

    for speaker in subspeakers:
        args.extend([('subspkip', speaker['ip'], 'str'), ('subspkmacaddr', speaker['mac'], 'str')])

    return ApiCall(api_type='UIC',
                   pwron=True,
                   method='SetMultispkGroup',
                   args=args,  # type: ignore
                   expected_response='MultispkGroup',
                   user_check=False,
                   timeout_multiple=3,
                   )


def set_multispk_group_subspk(name: str,
                              spknum: int,
                              mainspkip: str,
                              mainspkmacaddr: str,
                              ) -> ApiCall:
    """ (UIC) Group speakers.

    To be sent to all slaves in a group. Seems to be optional!

    Arguments:
        name:
            Group name.
        spknum:
            Number of speakers in the group.
        mainspkip:
            IP address to master speaker.
        mainspkmacaddr:
            MAC  address to master speaker.

    Notes:
        Following API-attributes does not seem to change and is therefore not
        arguments to this ApiCall factory.

        index:
            "1" always works
        type:
            "sub" because this is for the slave speaker.
        audiosourcetype:
            Should be "speaker". Have not found any information about
            optional values.
    """
    return ApiCall(api_type='UIC',
                   pwron=True,
                   method='SetMultispkGroup',
                   args=[('name', name, 'cdata'),
                         ('index', 1, 'dec'),
                         ('type', 'sub', 'str'),
                         ('spknum', spknum, 'dec'),
                         ('mainspkip', mainspkip, 'str'),
                         ('mainspkmacaddr', mainspkmacaddr, 'str'),
                         ],
                   user_check=False,
                   timeout_multiple=3,
                   )


def set_ungroup() -> ApiCall:
    """ (UIC) Ungroup speakers """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='SetUngroup',
                   args=[],
                   expected_response='Ungroup',
                   user_check=False,
                   timeout_multiple=1,
                   )


# **********************************************************************
# Equalizer
# **********************************************************************

def get_current_eq_mode() -> ApiCall:
    """ (UIC) Retrieve current equalizer settings. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='GetCurrentEQMode',
                   args=[],
                   expected_response='CurrentEQMode',
                   user_check=False,
                   timeout_multiple=1,
                   )


def get_7band_eq_list() -> ApiCall:
    """ (UIC) Retrieve stored equalizer presets. """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='Get7BandEQList',
                   args=[],
                   expected_response='7BandEQList',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_7band_eq_mode(presetindex: int) -> ApiCall:
    """ (UIC) Change equalizer values to a saved preset.

    Arguments:
        presetindex:
            Index of preset.
    """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='Set7bandEQMode',
                   args=[('presetindex', presetindex, 'dec')],
                   expected_response='7bandEQMode',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_7band_eq_value(presetindex: int,
                       eqvalue1: int,
                       eqvalue2: int,
                       eqvalue3: int,
                       eqvalue4: int,
                       eqvalue5: int,
                       eqvalue6: int,
                       eqvalue7: int,
                       ) -> ApiCall:
    """ (UIC) Change equalizer values to a new values.

    Arguments:
        presetindex:
            Index of preset to temporarily change.
            Safest is to find out current preset and use that.
        eqvalue1:
            150 Hz, value between -6 and 6.
        eqvalue2:
            300 Hz, value between -6 and 6.
        eqvalue3:
            600 Hz, value between -6 and 6.
        eqvalue4:
            1.2 kHz, value between -6 and 6.
        eqvalue5:
            2.5 kHz, value between -6 and 6.
        eqvalue6:
            5.0 kHz, value between -6 and 6.
        eqvalue7:
            10 kHz Hz, value between -6 and 6.
    """
    return ApiCall(api_type='UIC',
                   pwron=False,
                   method='Set7bandEQValue',
                   args=[('presetindex', presetindex, 'dec'),
                         ('eqvalue1', eqvalue1, 'dec'),
                         ('eqvalue2', eqvalue2, 'dec'),
                         ('eqvalue3', eqvalue3, 'dec'),
                         ('eqvalue4', eqvalue4, 'dec'),
                         ('eqvalue5', eqvalue5, 'dec'),
                         ('eqvalue6', eqvalue6, 'dec'),
                         ('eqvalue7', eqvalue7, 'dec'),
                         ],
                   expected_response='7bandEQValue',
                   user_check=False,
                   timeout_multiple=1,
                   )


# **********************************************************************
# Browsing
# **********************************************************************

def set_locale(locale: str) -> ApiCall:
    """ (CPM) Change speaker locale.

    Only known app to support is TuneIn. Used to get local radio
    stations when browsing.

    Arguments:
        locale:
            (eg: 'en-US', 'de-DE', 'sv-SE' )
    """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='SetLocale',
                   args=[('locale', locale, 'str')],
                   expected_response='LocaleChange',
                   user_check=False,
                   timeout_multiple=1,
                   )


def browse_main(startindex: int, listcount: int) -> ApiCall:
    """ (CPM) Browse TuneIn from the root.

    Arguments:
        startindex:
            Were to start. Should always be 0.
        listcount:
            Number of items to get.
    """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='BrowseMain',
                   args=[('startindex', startindex, 'dec'),
                         ('listcount', listcount, 'dec'),
                         ],
                   expected_response='RadioList',
                   user_check=True,
                   timeout_multiple=1,
                   )


def get_upper_radio_list(startindex: int, listcount: int) -> ApiCall:
    """ (CPM) Browse parent of a browsed TuneIn folder.

    Arguments:
        startindex:
            Were to start. Should always be 0.
        listcount:
            Number of items to get.
    """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='GetUpperRadioList',
                   args=[('startindex', startindex, 'dec'),
                         ('listcount', listcount, 'dec'),
                         ],
                   expected_response='RadioList',
                   user_check=True,
                   timeout_multiple=1,
                   )


def get_current_radio_list(startindex: int, listcount: int) -> ApiCall:
    """ (CPM) Browse current TuneIn folder.

    Arguments:
        startindex:
            Were to start. Should always be 0.
        listcount:
            Number of items to get. Android app use 30 as value.
    """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='GetCurrentRadioList',
                   args=[('startindex', startindex, 'dec'),
                         ('listcount', listcount, 'dec'),
                         ],
                   # TODO: Expected response
                   expected_response='',
                   user_check=True,
                   timeout_multiple=1,
                   )


def get_select_radio_list(contentid: int, startindex: int, listcount: int) -> ApiCall:
    """ (CPM) Select and browse a TuneIn folder.

    Arguments:
        contentid:
            ID of folder to browse. Should be in a folder previous browsed
            with this API call or with :browse_main():.
        startindex:
            Were to start. Should always be 0.
        listcount:
            Number of items to get.
    """
    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='GetSelectRadioList',
                   args=[('contentid', contentid, 'dec'),
                         ('startindex', startindex, 'dec'),
                         ('listcount', listcount, 'dec'),
                         ],
                   # TODO: Expected response
                   expected_response='',
                   user_check=False,
                   timeout_multiple=1,
                   )


def set_play_select(select_item_ids: int | list[int]) -> ApiCall:
    """ (CPM) Plays selected TuneIn or app items.

    Arguments:
        select_item_ids:
            Content id returned by get_upper_radio_list(),
            get_select_radio_list() or get_current_radio_list(),
            or list of content ids
    """
    if isinstance(select_item_ids, list):
        method = 'selectitemids'
        arg_type = 'dec_arr'
    else:
        method = 'selectitemid'
        arg_type = 'dec'

    return ApiCall(api_type='CPM',
                   pwron=False,
                   method='SetPlaySelect',
                   args=[(method, select_item_ids, arg_type)],
                   # TODO: Expected response
                   expected_response='',
                   user_check=False,
                   timeout_multiple=1,
                   )
