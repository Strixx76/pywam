# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Storing speaker state and attributes. """
from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from pywam.lib import translate
from pywam.lib.equalizer import EqualizerPreset, EqualizerValues
from pywam.lib.media_presets import MediaPreset


if TYPE_CHECKING:
    from datetime import datetime
    from pywam.speaker import Speaker


class WamAttributes:
    """ Stores speaker attributes.

    Attributes is updated by the event handler, WamEvents.
    All attribute values is stored as private attributes with original
    API response values. The values is then converted to user values in
    the property methods.

    Attributes:
        _spkname:
            Speaker name.
        _spkmacaddr:
            Speakers ethernet MAC address.
        _spkmodelname:
            Speaker model.
        _device_id:
            Speaker API device ID.
        _btmacaddr:
            Speakers bluetooth MAC address.
        _displayversion:
            Version of firmware.
        _ch(str):
            WiFi channel used. "0" if ethernet.
        _connectiontype(str):
            "ethernet" | ""wireless"".
        _rssi(str):
            RSSI. Seen values 2, 3 and 4. "None" if ethernet.
        _ssid(str):
            SSID. "None" if ethernet.
        _iptable:
            List of all connected clients.
        _groupmainip:
            Master speaker IP when grouped.
            '0.0.0.0' if not grouped is returned by MainInfo.
            Will be None if speaker is Master but returned from MultispkGroup-event.
            Will be own IP if speaker is Master and returned from MainInfo-event.
        _groupmainmacaddr:
            Master speaker MAC when grouped
            '0.0.0.0' if not grouped is returned by MainInfo.
            Will be None if speaker is Master but returned from MultispkGroup-event.
            Will be own MAC if speaker is Master and returned from MainInfo-event.
        _groupspknum:
            Total number of speakers in the group.
            Called spknum in MultispkGroup events but stored here.
        _grouptype:
            'M'|'S'|'N' = Master, Slave, None (if not in group).
        _groupname:
            Name of speaker group or 'None'. If received by MultispkGroup-event
            slaves will not know the groupname and GetGroupName-call must be sent.
        _volume:
            Speaker volume between 0 and 30.
        _mute:
            Mute state - 'on'|'off' - 'on' = muted.
        _playstatus:
            Player status - 'stop'|'pause'|'play'
        _repeat:
            Repeat mode - 'one'|'all'|'off'
        _shuffle:
            Shuffle mode - 'on'|'off' - 'on'
        _function:
            Current selected source.
        _submode:
            'cp'|'dlna'|'subdevice'|'None'
            Other projects also have: 'dmr', 'device'
        _connection:
            'on'|'off'|'None' (On when BT is connected)
        _devicename:
            Name of connected BT device.
        _cpname:
            Music service provider active on the speaker.
        _title:
            Song title or title of radio station.
        _description:
            Description of the radio, can include the currently played song.
        _artist:
            Name of artist.
        _album:
            Name of album playing.
        _thumbnail:
            HTTP address to thumbnail picture.
        _tracklength:
            Length of track in seconds.
        _eqmode_presetlist:
            List of stored equalizer presets on the speaker.
        _presetname:
            Name of active equalizer preset.
        _eqvalue1:
            150 Hz, value between -6 and 6.
        _eqvalue2:
            300 Hz, value between -6 and 6.
        _eqvalue3:
            600 Hz, value between -6 and 6.
        _eqvalue4:
            1.2 kHz, value between -6 and 6.
        _eqvalue5:
            2.5 kHz, value between -6 and 6.
        _eqvalue6:
            5.0 kHz, value between -6 and 6.
        _eqvalue7:
            10 kHz, value between -6 and 6.
        _media_presetlist:
            cpname:
                contentid(str):
                    No in preset list, use this to play the station.
                description(str):
                    Station description.
                kind(str):
                    Either 'speaker' or 'my'.
                    For `contentid` 0-2 `kind` is 'my',
                    and for `contentid` > 2 `kind` is 'speaker'.
                mediaid(str):
                    Id on TuneIn
                thumbnail(str):
                    URL to station logo thumbnail.
                title(str):
                    Title of radio station.
        _last_seen:
            Timestamp when speaker was last heard from.
    """

    def __init__(self, speaker: Speaker) -> None:

        self._speaker = speaker

        # UNMODIFIED WAM ATTRIBUTES
        # Speaker attributes
        self._spkname: str | None = None
        self._spkmacaddr: str | None = None
        self._spkmodelname: str | None = None
        self._device_id: str | None = None
        self._btmacaddr: str | None = None
        self._displayversion: str | None = None
        self._connectiontype: str | None = None
        self._ch: str | None = None
        self._rssi: str | None = None
        self._ssid: str | None = None
        self._iptable: list[dict[str, str]] | None = None
        # Grouping
        self._grouptype: str | None = None
        self._groupname: str | None = None
        self._groupmainip: str | None = None
        self._groupmainmacaddr: str | None = None
        self._groupspknum: str | None = None
        # Player attributes
        self._volume: str | None = None
        self._mute: str | None = None
        self._playstatus: str | None = None
        self._repeat: str | None = None
        self._shuffle: str | None = None
        # Source
        self._function: str | None = None
        self._submode: str | None = None
        self._connection: str | None = None
        self._devicename: str | None = None
        self._cpname: str | None = None
        # Media attributes
        self._title: str | None = None
        self._description: str | None = None
        self._artist: str | None = None
        self._album: str | None = None
        self._thumbnail: str | None = None
        self._tracklength: str | None = None
        # Equalizer / Sound mode
        self._eqmode_presetlist: list[dict[str, str]] | None = None
        self._presetname: str | None = None
        self._eqvalue1: str | None = None
        self._eqvalue2: str | None = None
        self._eqvalue3: str | None = None
        self._eqvalue4: str | None = None
        self._eqvalue5: str | None = None
        self._eqvalue6: str | None = None
        self._eqvalue7: str | None = None

        # MODIFIED SPEAKER PROPERTIES
        # Media presets (media/app/channel favorites)
        self._media_presetlist: dict[str, list[dict[str, str]]] = {}
        # PYWAM ATTRIBUTES
        self._last_seen: datetime | None = None

    def __str__(self):
        return str(self.get_state_copy())

    def _get_int_state_copy(self) -> dict:
        """ Returns a copy of all WAM state attributes.

        Only to be used for debugging purpose.
        """
        return {
            '_spkname': self._spkname,
            '_spkmacaddr': self._spkmacaddr,
            '_spkmodelname': self._spkmodelname,
            '_device_id': self._device_id,
            '_btmacaddr': self._btmacaddr,
            '_displayversion': self._displayversion,
            '_connectiontype': self._connectiontype,
            '_ch': self._ch,
            '_rssi': self._rssi,
            '_ssid': self._ssid,
            '_iptable': self._iptable,

            '_grouptype': self._grouptype,
            '_groupname': self._groupname,
            '_groupmainip': self._groupmainip,
            '_groupmainmacaddr': self._groupmainmacaddr,
            '_groupspknum': self._groupspknum,

            '_volume': self._volume,
            '_mute': self._mute,
            '_playstatus': self._playstatus,
            '_repeat': self._repeat,
            '_shuffle': self._shuffle,

            '_function': self._function,
            '_submode': self._submode,
            '_connection': self._connection,
            '_devicename': self._devicename,
            '_cpname': self._cpname,

            '_title': self._title,
            '_description': self._description,
            '_artist': self._artist,
            '_album': self._album,
            '_thumbnail': self._thumbnail,
            '_tracklength': self._tracklength,

            '_presetname': self._presetname,
            '_eqvalue1': self._eqvalue1,
            '_eqvalue2': self._eqvalue2,
            '_eqvalue3': self._eqvalue3,
            '_eqvalue4': self._eqvalue4,
            '_eqvalue5': self._eqvalue5,
            '_eqvalue6': self._eqvalue6,
            '_eqvalue7': self._eqvalue7,
            '_eqmode_presetlist': copy.deepcopy(self._eqmode_presetlist),

            '_media_presetlist': copy.deepcopy(self._media_presetlist),

            '_last_seen': self._last_seen,
        }

    @ property
    def name(self) -> str | None:
        """ Return speaker's name. """
        return self._spkname

    @ property
    def mac(self) -> str | None:
        """ Return speaker network adaptor mac address. """
        return self._spkmacaddr

    @ property
    def model(self) -> str | None:
        """ Return speaker model. """
        return translate.model()

    @ property
    def device_id(self) -> str | None:
        """ Return speaker ID. """
        return self._device_id

    @ property
    def bt_mac(self) -> str | None:
        """ Return speaker BT mac address. """
        return self._btmacaddr

    @ property
    def software_version(self) -> str | None:
        """ Return software version on speaker. """
        return self._displayversion

    @ property
    def connection_type(self) -> str | None:
        """ Return type of network connection. """
        return self._connectiontype

    @ property
    def wifi_channel(self) -> str | None:
        """ Return WiFi channel if connect with WiFi. """
        return self._ch

    @ property
    def wifi_rssi(self) -> str | None:
        """ Return RSSI (0-5)? if connect with WiFi. """
        return self._rssi

    @ property
    def wifi_ssid(self) -> str | None:
        """ Return SSID if connect with WiFi. """
        return self._ssid

    @ property
    def clients(self) -> dict[str, str] | None:
        """ Return a dictionary of connected clients.

        Returns:
            {"IP address": "UUID"}
        """
        if not self._iptable:
            return None
        clients = {}
        for client in self._iptable:
            clients[client.get('ip', 'unknown')] = client.get('@uuid', '')
        return clients

    @property
    def is_grouped(self) -> bool | None:
        """ True if the speaker is grouped. """
        if self._groupspknum is None or self._grouptype is None:
            return None
        if self._groupspknum == '1':
            return False
        if self._grouptype == 'N':
            return False

        return True

    @ property
    def is_master(self) -> bool | None:
        """ True if the speaker is master in a group. """
        if not self._grouptype:
            return None
        return (self._grouptype == 'M')

    @ property
    def is_slave(self) -> bool | None:
        """ True if the speaker is slave in a group. """
        if not self._grouptype:
            return None
        return (self._grouptype == 'S')

    @ property
    def group_name(self) -> str | None:
        """ Return group's name. """
        return self._groupname

    @ property
    def master_ip(self) -> str | None:
        """ Returns masters IP address if slave and grouped.. """
        # When master it could either be own IP or None depending on
        # last received event
        if self.is_slave:
            return self._groupmainip
        return None

    @ property
    def master_mac(self) -> str | None:
        """ Returns masters MAC address if speaker is grouped. """
        # When master it could either be own MAC or None depending on
        # last received event
        if self.is_slave:
            return self._groupmainmacaddr
        return None

    @ property
    def number_of_speakers(self) -> int | None:
        """ Returns number of speakers in group if grouped. """
        if self._groupspknum is not None:
            return int(self._groupspknum)
        return None

    @ property
    def volume(self) -> int | None:
        """ Return volume level (0-100). """
        if self._volume is not None:
            return translate.decode_volume(int(self._volume))
        return None

    @ property
    def muted(self) -> bool | None:
        """ Return True if speaker is muted. """
        if not self._mute:
            return None
        return (self._mute == 'on')

    @ property
    def state(self) -> str | None:
        """ Return speaker state.

        Possible values are:  'stop' | 'play' | 'pause' | 'resume'
        """
        return self._playstatus

    @ property
    def repeat_mode(self) -> str | None:
        """ Return current repeat mode. ('all'|'one'|'off'). """
        return self._repeat

    @ property
    def shuffle_mode(self) -> bool | None:
        """ Return current shuffle mode. """
        if not self._shuffle:
            return None
        return (self._shuffle == 'on')

    @ property
    def source_list(self) -> list[str]:
        """ Return selectable speaker input sources. """
        return translate.sources()

    @ property
    def source(self) -> str | None:
        """ Return current selected input source. """
        if not self._function:
            return None
        return translate.decode_source(self._function)

    @ property
    def app_name(self) -> str | None:
        """ Return name of the current playing app."""
        # Only on WiFi apps can be playing
        if self._function != 'wifi':
            return None

        if self._submode == 'cp':
            return self._cpname
        elif self._submode == 'dlna':
            return 'DLNA'
        elif self._submode == 'url':
            return 'URL Playback'

        return None

    @ property
    def media_title(self) -> str | None:
        """ Return title of media, radio station or connected BT device. """
        return self._title or self._devicename

    @ property
    def media_artist(self) -> str | None:
        """ Return artist or description of radio station. """
        return self._artist or self._description

    @ property
    def media_album_name(self) -> str | None:
        """ Return album name of current playing media. """
        return self._album

    @ property
    def media_album_artist(self) -> str | None:
        """ Return album artist of current playing media. """
        # TODO: Implement
        return None

    @ property
    def media_track(self) -> int | None:
        """ Return track number of current playing media. """
        # TODO: Implement
        return None

    @ property
    def media_image_url(self) -> str | None:
        """ Return url to image fo current playing media. """
        if self._thumbnail:
            if self._thumbnail.startswith('http'):
                return self._thumbnail
        return None

    @ property
    def media_duration(self) -> int | None:
        """ Return duration of current playing media in seconds. """
        if self._tracklength:
            return int(self._tracklength)
        else:
            return None

    @ property
    def media_position(self) -> int | None:
        """ Return position of current playing media in seconds. """
        # TODO: Implement
        return None

    @ property
    def sound_mode_list(self) -> list[EqualizerPreset]:
        """ Return equalizer presets stored on speaker. """
        if not self._eqmode_presetlist:
            return []
        return [EqualizerPreset(**preset) for preset in self._eqmode_presetlist]

    @ property
    def sound_mode(self) -> str | None:
        """ Return name of current used equalizer values. """
        return self._presetname

    @ property
    def equalizer_values(self) -> EqualizerValues | None:
        """ Return current equalizer values. """
        eqvalues = {'hz_150': self._eqvalue1,
                    'hz_300': self._eqvalue2,
                    'hz_600': self._eqvalue3,
                    'hz_1200': self._eqvalue4,
                    'hz_2500': self._eqvalue5,
                    'hz_5000': self._eqvalue6,
                    'hz_10000': self._eqvalue7,
                    }
        if None in eqvalues.values():
            return None

        return EqualizerValues(**eqvalues)  # type: ignore

    @ property
    def tunein_presets(self) -> list[MediaPreset]:
        """ Return TuneIn presets stored in speaker. """
        if not self._media_presetlist:
            return []
        app = 'TuneIn'
        return [MediaPreset(cpname=app, **preset) for preset in self._media_presetlist[app]]

    @ property
    def last_seen(self) -> datetime | None:
        """ When was the speaker last seen. """
        return self._last_seen

    def get_state_copy(self) -> dict:
        """ Returns a copy of all attributes as dictionary. """
        return {
            'name': self.name,
            'mac': self.mac,
            'model': self.model,
            'device_id': self.device_id,
            'bt_mac': self.bt_mac,
            'software_version': self.software_version,
            'connection_type': self.connection_type,
            'wifi_channel': self.wifi_channel,
            'wifi_rssi': self.wifi_rssi,
            'wifi_ssid': self.wifi_ssid,
            'clients': copy.deepcopy(self.clients),
            'is_master': self.is_master,
            'is_slave': self.is_slave,
            'group_name': self.group_name,
            'master_ip': self.master_ip,
            'master_mac': self.master_mac,
            'number_of_speakers': self.number_of_speakers,
            'volume': self.volume,
            'muted': self.muted,
            'state': self.state,
            'repeat_mode': self.repeat_mode,
            'shuffle_mode': self.shuffle_mode,
            'source_list': list(self.source_list),
            'source': self.source,
            'app_name': self.app_name,
            'media_title': self.media_title,
            'media_artist': self.media_artist,
            'media_album_name': self.media_album_name,
            'media_album_artist': self.media_album_artist,
            'media_track': self.media_track,
            'media_image_url': self.media_image_url,
            'media_duration': self.media_duration,
            'media_position': self.media_position,
            'sound_mode_list': copy.deepcopy(self.sound_mode_list),
            'sound_mode': self.sound_mode,
            'tunein_presets': copy.deepcopy(self.tunein_presets),
        }

    def reset_source_info(self) -> None:
        """ Reset all attributes containing source info. """
        self._function = None
        self._submode = None
        self._connection = None
        self._devicename = None
        self._cpname = None

    def reset_media_info(self) -> None:
        """ Reset all attributes containing playing media info. """
        self._cpname = None
        self._playstatus = None
        self._title = None
        self._description = None
        self._artist = None
        self._album = None
        self._thumbnail = None
        self._tracklength = None
