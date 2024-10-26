# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

# pylint: disable=W0212:protected-access
# pylint: disable=W0613:unused-argument
# pylint: disable=C0103:invalid-name
# pylint: disable=C0302:too-many-lines
""" Checking for state/attribute changes. """
from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

from pywam.lib.validate import is_integer
from pywam.lib.helpers import listify

if TYPE_CHECKING:
    from pywam.lib.api_response import ApiResponse
    from pywam.speaker import Speaker

_LOGGER = logging.getLogger(__name__)


class WamEvents:
    """ Handles events from speaker.

    Arguments:
        attributes:
            WamAttributes object shared with Speaker object.
    """

    def __init__(self, speaker: Speaker):
        self._attr = speaker.attribute
        self._speaker = speaker
        self._subscriber: dict[Callable, int] = {}
        self._latest_known_state: dict = self._attr.get_state_copy()

    def receiver(self, event: 'ApiResponse') -> None:
        """ Receives events from WamClient.

        Arguments:
            event:
                ApiResponse object with information about the event.
        """
        _LOGGER.debug('(%s) Event handler received an event', self._speaker.ip)
        _LOGGER.debug('Event: %s', event)

        # Don't do anything with unsuccessful responses. Empty events
        # can mess upp stored state of speaker.
        if not event.success:
            return

        # Call corresponding method for events from speaker.
        event_method = getattr(self, 'event_' + event.method, None)
        if not event_method:
            _LOGGER.info('(%s) Event handler received an unknown event', self._speaker.ip)
            _LOGGER.info('Event: %s', event)
            return
        used = event_method(event)

        self._attr._last_seen = datetime.now()

        # Send the event
        self._dispatch_event(used, event)

    # ******************************************************************
    # Methods for handling event subscriber
    # ******************************************************************

    def _dispatch_event(self, used: bool, event: 'ApiResponse') -> None:
        """ Send events to subscriber. """
        for subscriber, info_level in self._subscriber.items():
            try:
                if info_level == 2:
                    subscriber(event)
                    return
                if used:
                    old = self._latest_known_state
                    new = self._attr.get_state_copy()
                    if new == old:
                        return
                    if info_level == 1:
                        changed = {key: new[key] for key in old if new[key] != old[key]}
                        subscriber(changed)
                    if info_level == 0:
                        subscriber()
                    self._latest_known_state = new
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception('(%s) Could not dispatch event from speaker', self._speaker.ip)

    def register_subscriber(self,
                            callback: Callable[[], Any] | Callable[[dict], Any],
                            info_level: int = 0,
                            ) -> None:
        """ Register subscriber for speaker attribute changes.

        Arguments:
            callback:
                Callable to be called when a speaker attribute changes.
            info_level (optional):
                0 = Callback will be called without any args when the
                speaker get an updated attribute.
                1 = Callback will be called with one argument containing
                a dictionary with all the attributes that has changed
                since last call.
                2 = Callback will be called on all received events even
                if there was no attributes changed, and the ApiResponse
                object will be passed as first argument.
                Defaults to 0.

        Raises:
            TypeError: If given argument is not a callable.
        """
        if not callable(callback):
            raise TypeError('Subscriber must be a callable')
        info_level = is_integer(info_level, (0, 2))
        self._subscriber[callback] = info_level

    def unregister_subscriber(self, callback: Callable) -> None:
        """ Unregister subscriber.

        Arguments:
            callback:
                Previously registered callback to unregister.

        Raises:
            KeyError: If callback is not a registered subscriber.
        """
        try:
            del self._subscriber[callback]
        except KeyError as e:
            raise KeyError(f'{callback} is not a registered subscriber') from e

    # ******************************************************************
    # Speaker events
    # ******************************************************************

    # TODO: Events not discovered yet, but present in other projects:
    # PowerStatus, RearLevel, ToggleShuffle, AmazonCpSelected, SkipInfo
    # SubMenu, ErrorEvent, RadioPlayList

    def event_7BandEQList(self, event: 'ApiResponse') -> bool:
        """ List of all equalizer presets on the speaker.

        method (str): '7BandEQList'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            listcount(str):
                Number of preset in list.
            presetlist(dict):
                preset(list):
                        @index(str):
                            Index of preset.
                        presetindex(str):
                            Index of preset. Used for selecting preset.
                        presetname(str):
                            Name of preset.
            presetlistcount(str):
                ???? (Always "4"?)
        """
        self._attr._eqmode_presetlist = listify(event.get_subkey('presetlist', 'preset'))
        return True

    def event_7bandEQMode(self, event: 'ApiResponse') -> bool:
        """ Current EQ settings for speaker.

        Same attributes as 'CurrentEQMode'. Don't know when which is
        sent.

        method (str): '7bandEQMode'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            eqvalue1(str):
                150 Hz, value between -6 and 6.
            eqvalue2(str):
                300 Hz, value between -6 and 6.
            eqvalue3(str):
                600 Hz, value between -6 and 6.
            eqvalue4(str):
                1.2 kHz, value between -6 and 6.
            eqvalue5(str):
                2.5 kHz, value between -6 and 6.
            eqvalue6(str):
                5.0 kHz, value between -6 and 6.
            eqvalue7(str):
                10 kHz, value between -6 and 6.
            presetindex(str):
                Index in '7BandEQList'.
            presetname(str):
                Name of EQ-preset.
        """
        self._attr._presetname = event.get_key('presetname')
        self._attr._eqvalue1 = event.get_key('eqvalue1')
        self._attr._eqvalue2 = event.get_key('eqvalue2')
        self._attr._eqvalue3 = event.get_key('eqvalue3')
        self._attr._eqvalue4 = event.get_key('eqvalue4')
        self._attr._eqvalue5 = event.get_key('eqvalue5')
        self._attr._eqvalue6 = event.get_key('eqvalue6')
        self._attr._eqvalue7 = event.get_key('eqvalue7')
        return True

    def event_7bandEQValue(self, event: 'ApiResponse') -> bool:
        """ Current EQ settings for speaker.

        This one is sent when current setting is not an preset.

        method (str): '7bandEQValue'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            eqvalue1(str):
                150 Hz, value between -6 and 6.
            eqvalue2(str):
                300 Hz, value between -6 and 6.
            eqvalue3(str):
                600 Hz, value between -6 and 6.
            eqvalue4(str):
                1.2 kHz, value between -6 and 6.
            eqvalue5(str):
                2.5 kHz, value between -6 and 6.
            eqvalue6(str):
                5.0 kHz, value between -6 and 6.
            eqvalue7(str):
                10 kHz, value between -6 and 6.
            presetindex(str):
                Always '0'?
        """
        self._attr._presetname = None
        self._attr._eqvalue1 = event.get_key('eqvalue1')
        self._attr._eqvalue2 = event.get_key('eqvalue2')
        self._attr._eqvalue3 = event.get_key('eqvalue3')
        self._attr._eqvalue4 = event.get_key('eqvalue4')
        self._attr._eqvalue5 = event.get_key('eqvalue5')
        self._attr._eqvalue6 = event.get_key('eqvalue6')
        self._attr._eqvalue7 = event.get_key('eqvalue7')
        return True

    def event_AcmMode(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AcmMode'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            acmmode(str):
            audiosourcemacaddr(str):
            audiosourcename(str):
            audiosourcetype(str):
        """
        return False

    def event_AddCustomEQMode(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AddCustomEQMode'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            presetindex(str):
            presetname(str):
        """
        return False

    def event_AddSongsToMultiQueueResult(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AddSongsToMultiQueueResult'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            count(str):
            curindex(str):
            seqcount(str):
            startindex(str):
            totalcount(str):
        """
        return False

    def event_AlarmInfo(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AlarmInfo'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            alarm(str):
            description(str):
            duration(str):
            hour(str):
            index(str):
            min(str):
            sound(str):
            soundenable(str):
            stationurl(str):
            thumbnail(str):
            title(str):
            volume(str):
            week(str):
        """
        return False

    def event_AlarmOnOff(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AlarmOnOff'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            alarm(str):
            index(str):
        """
        return False

    def event_AlarmSoundList(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AlarmSoundList'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            alarmlist(dict):
                alarmsound(list):
                        @index(str):
                        alarmsoundname(str):
                        alarsoundindex(str):
            listcount(str):
        """
        return False

    def event_AllAlarmInfo(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AllAlarmInfo'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            alarmList(str | dict):
                alarm(dict | list):
                        @index(str):
                        alarmsoundname(str):
                        description(str):
                        duration(str):
                        hour(str):
                        min(str):
                        set(str):
                        sound(str):
                        soundenable(str):
                        stationurl(str):
                        thumbnail(str):
                        title(str):
                        volume(str):
                        week(str):
                    @index(str):
                    alarmsoundname(str):
                    description(str):
                    duration(str):
                    hour(str):
                    min(str):
                    set(str):
                    sound(str):
                    soundenable(str):
                    stationurl(str):
                    thumbnail(str):
                    title(str):
                    volume(str):
                    week(str):
            totalindexcount(str):
        """
        return False

    def event_ApInfo(self, event: 'ApiResponse') -> bool:
        """ Information about network connection.

        method (str): 'ApInfo'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            ch(str):
                WiFi channel used. "0" if ethernet.
            connectiontype(str):
                "ethernet" | ""wireless"".
            mac(str):
                Speaker MAC address.
            rssi(str):
                RSSI. Seen values 2, 3 and 4. "None" if ethernet.
            ssid(str):
                SSID. "None" if ethernet.
            wifidirectch(str):
                ????
            wifidirectrssi(str):
                ????
            wifidirectssid(str):
                ????
        """
        self._attr._ch = event.get_key('ch')
        self._attr._connectiontype = event.get_key('connectiontype')
        self._attr._rssi = event.get_key('rssi')
        self._attr._ssid = event.get_key('ssid')
        return False

    def event_AudioUI(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AudioUI'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            audioui(str):
        """
        return False

    def event_AutoUpdate(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AutoUpdate'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            autoupdate(str):
        """
        return False

    def event_AvSourceAll(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'AvSourceAll'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            avsourcelist(str):
            listcount(str):
        """
        return False

    def event_AvSourceAddedEvent(self, event: 'ApiResponse') -> bool:
        """ Found new AV-source on the network.

        method (str): 'AvSourceAddedEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            avdeviceip(str):
                IP address of the new AV-source
            avdevicemacaddr(str):
                MAC address of the new AV-source
            avdevicename(str):
                Name of the new AV-source
            avdevicetype(str):
                Type of AV-source ('tv')
            avdevicemultichinfo(str):
                'on'
            dfsstatus(str):
                'dfsoff'
        """
        return False

    def event_AvSourceDeletedEvent(self, event: 'ApiResponse') -> bool:
        """ AV-source disappeared from on the network.

        method (str): 'AvSourceDeletedEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            avdeviceip(str):
                IP address of the new AV-source
            avdevicemacaddr(str):
                MAC address of the new AV-source
            avdevicename(str):
                Name of the new AV-source
            avdevicetype(str):
                Type of AV-source ('tv')
            avdevicemultichinfo(str):
                'on'
        """
        return False

    def event_BatteryStatus(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'BatteryStatus'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            batterymode(str):
            batteryrate(str):
        """
        return False

    def event_ChVolMultich(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'ChVolMultich'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            channelvolume(str):
        """
        return False

    def event_ConnectionStatus(self, event: 'ApiResponse') -> bool:
        """ Device connected to speaker.

        Sent when a Bluetooth device connects to or disconnects from
        the speaker.

        method (str): 'ConnectionStatus'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            function(str):
                'bt'
            connection(str):
                'on' | 'off'
            devicename(str):
                Name of connected device.
        """
        self._attr.reset_source_info()
        self._attr.reset_media_info()
        self._attr._devicename = event.get_key('devicename')
        self._attr._connection = event.get_key('connection')
        self._attr._function = event.get_key('function')
        return True

    def event_CpChanged(self, event: 'ApiResponse') -> bool:
        """ Another cp service was selected.

        Sent when a new cp is selected for browsing or searching.

        method (str): 'CpChanged'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            cpname(str):
        """
        return False

    def event_CpInfo(self, event: 'ApiResponse') -> bool:
        """ Currently selected cp service.

        The cpm app selected for doing operations, and not what is
        playing on the speaker. You could have 'Spotify' selected and at
        the same time playing a TuneIn radio channel, or vice versa.

        method (str): 'CpInfo'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            audioinfo(dict, optional):
                playstatus(str, optional):
                    'stop'|'pause'|'play' (Only if 'cpname' is 'TuneIn'.)
                thumbnail(str):
                    HTTP address to thumbnail picture.
                title(str):
                    Song title or title of radio station.
            category(str, optional):
                ?
            cpname(str):
                Selected CP service.
            device_id(str, optional):
                ?
            playstatus(str, optional):
                'stop'|'pause'|'play' (If 'cpname' is other than 'TuneIn')
            root(str, optional):
                ?
            signinstatus(str, optional):
                '0' | '1' - 1 if signed in
            timestamp(str, optional):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
            username(str, optional):
                Username that is signed in
        """
        return False

    def event_CpList(self, event: 'ApiResponse') -> bool:
        """ List all available music service providers.

        method (str): 'CpList'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            cplist(dict):
                cp(list):
                        cpid(str):
                        cpname(str):
                        istrial_user(str, optional):
                        signinstatus(str):
                        username(str, optional):
            listcount(str):
            liststartindex(str):
            listtotalcount(str):
        """
        return False

    def event_CurrentEQMode(self, event: 'ApiResponse') -> bool:
        """ Current EQ settings for speaker.

        Same as attributes as '7bandEQMode'. Don't know when which is
        sent.

        method (str): 'CurrentEQMode'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            eqvalue1(str):
                150 Hz, value between -6 and 6.
            eqvalue2(str):
                300 Hz, value between -6 and 6.
            eqvalue3(str):
                600 Hz, value between -6 and 6.
            eqvalue4(str):
                1.2 kHz, value between -6 and 6.
            eqvalue5(str):
                2.5 kHz, value between -6 and 6.
            eqvalue6(str):
                5.0 kHz, value between -6 and 6.
            eqvalue7(str):
                10 kHz, value between -6 and 6.
            presetindex(str):
                Index in '7BandEQList'.
            presetname(str):
                Name of EQ-preset.
        """
        self._attr._presetname = event.get_key('presetname')
        self._attr._eqvalue1 = event.get_key('eqvalue1')
        self._attr._eqvalue2 = event.get_key('eqvalue2')
        self._attr._eqvalue3 = event.get_key('eqvalue3')
        self._attr._eqvalue4 = event.get_key('eqvalue4')
        self._attr._eqvalue5 = event.get_key('eqvalue5')
        self._attr._eqvalue6 = event.get_key('eqvalue6')
        self._attr._eqvalue7 = event.get_key('eqvalue7')
        return True

    def event_CurrentFunc(self, event: 'ApiResponse') -> bool:
        """ Current selected source for the speaker.

        Sent when asked for (´GetFunc´) or when changed (´SetFunc´).

        method (str): 'CurrentFunc'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'None' | 'UUID' | 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            connection(str):
                'on'|'off'|'None' (On when BT is connected)
            devicename(str):
                Name of connected BT device.
            function(str):
                Current selected source.
            submode(str):
                'cp'|'dlna'|'subdevice'|'None'
                (If 'function' != 'wifi', always 'None')
                Other projects also have: 'dmr', 'device'
        """
        # Workaround for UrlPlayback
        # If the native app is started we need to ignore the attributes
        # if we are playing a url.
        if event.get_key('submode') == 'cp' and self._attr._submode == 'url':
            return False

        function = event.get_key('function')
        if function != self._attr._function:
            self._attr.reset_media_info()
            self._attr._function = function
        self._attr._submode = event.get_key('submode')
        self._attr._connection = event.get_key('connection')
        self._attr._devicename = event.get_key('devicename')
        return True

    def event_DelAlarm(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'DelAlarm'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            index(list):
                '-1' | '0' | '1' | '2'
        """
        return False

    def event_DelCustomEQMode(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'DelCustomEQMode'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            presetindex(str):
            presetname(str):
        """
        return False

    def event_DelSongsFromMultiQueueResult(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'DelSongsFromMultiQueueResult'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            count(str):
            curindex(str):
            index(str, optional):
            seqcount(str):
            totalcount(str):
        """
        return False

    def event_DeviceId(self, event: 'ApiResponse') -> bool:
        """ Device ID.

        Speaker has three different ID.
         - Received from upnp/ssdp (13 char)
         - api_v2.json receieved from http://speaker.ip:8001/api/v2/
           (13 char)
         - This ID (12 char)

        method (str): 'DeviceId'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            device_id(str):
                Device ID
        """
        self._attr._device_id = event.get_key('device_id')
        return True

    def event_DMSAddedEvent(self, event: 'ApiResponse') -> bool:
        """ UIC - New DLNA server discovered.

        method (str): 'DMSAddedEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
        """
        return False

    def event_DMSDeletedEvent(self, event: 'ApiResponse') -> bool:
        """ UIC - DLNA removed from network.

        method (str): 'DMSDeletedEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            device_udn (str): Source device unique identifier.
        """
        return False

    def event_DmsList(self, event: 'ApiResponse') -> bool:
        """ UIC - DLNA servers found by the speaker.

        List all dlna music servers found by the speaker.

        method (str): 'DmsList'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            dmslist(dict):
                dms(dict):
                    @device_id(str):
                    devicetype(str):
                    dmsid(str):
                    dmsname(str):
                    thumbnail_JPG_LRG(str):
                    thumbnail_JPG_SM(str):
                    thumbnail_PNG_LRG(str):
                    thumbnail_PNG_SM(str):
            listcount(str):
            liststartindex(str):
            listtotalcount(str):
        """
        return False

    def event_EndPlaybackEvent(self, event: 'ApiResponse') -> bool:
        """ Start playback.

        Sent when stopping playback on the speaker.

        method (str): 'EndPlaybackEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            playtime(str):
                ?
        """
        self._attr._playstatus = 'stop'
        return True

    def event_EQDrc(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'EQDrc'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'None' | 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            eqdrc(str):
                Only seen 'off'.
        """
        return False

    def event_EQMode(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'EQMode'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            eqbalance(str):
                Only seen '0'.
            eqbass(str):
                Only seen '0'.
            eqdrc(str):
                Only seen 'on'.
            eqtreble(str):
                Only seen '0'.
        """
        return False

    def event_GlobalSearch(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'GlobalSearch'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        async_response:
        """
        return False

    def event_GroupName(self, event: 'ApiResponse') -> bool:
        """ Name of speaker group.

        method (str): 'GroupName'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID' | 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            groupname(str):
                Name of speaker group or 'None'.
        """
        self._attr._groupname = event.get_key('groupname')
        return True

    def event_IpInfo(self, event: 'ApiResponse') -> bool:
        """ List of all connected clients.

        method (str): 'IpInfo'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            iptablelist(dict):
                iptable(list):
                        @uuid(str):
                            Clients UUID
                        ip(str):
                            Clients IP address
            listcount(str):
        """
        self._attr._iptable = listify(event.get_subkey('iptablelist', 'iptable'))
        return True

    def event_KPIValue(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'KPIValue'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            kpi(str):
        """
        return False

    def event_LastMusicEvent(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'LastMusicEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (str):
        """
        return False

    def event_LedStatus(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'LedStatus'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            led(str):
        """
        return False

    def event_LocaleChange(self, event: 'ApiResponse') -> bool:
        """ Location changed.

        Sent when the location is change. Is used when browse and search
        TuneIn to get local radio stations.

        method (str): 'LocaleChange'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            cpname(str, optional):
        """
        return False

    def event_MainInfo(self, event: 'ApiResponse') -> bool:
        """ Main information about speaker.

        Sent as second response on API call ´GetMainInfo´.

        method (str): 'MainInfo'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            btmacaddr(str):
                Speakers bluetooth MAC address.
            channeltype(str):
                'front'|'fr'|'fl'|'invalid'
            channelvolume(str):
                '-6'|'0' ? Only when in stereo.
            dfsstatus(str):
                'dfson'|'dfsoff'
            groupmainip(str):
                Master speaker IP when grouped (otherwise '0.0.0.0').
            groupmainmacaddr(str):
                Master speaker MAC when grouped (otherwise '00:00:00:00:00:00').
            groupmode(str):
                'avsync'|'aasync'|'none' ('none' when not in group).
                NB! 'none' and not 'None'.
            groupspknum(str):
                Total number of speakers in the group.
            grouptype(str):
                'M'|'S'|'N' = Master, Slave, None (if not in group).
            multichinfo(str):
                Always 'on'?
            party(str):
                ? (Only seen 'off')
            partymain(str):
                ? (Only seen 'None')
            protocolver(str):
                Always '2.3'
            spkmacaddr(str):
                Speakers ethernet MAC address.
            spkmodelname(str):
                Speaker model.
        """
        self._attr._spkmacaddr = event.get_key('spkmacaddr', self._attr._spkmacaddr)
        self._attr._spkmodelname = event.get_key('spkmodelname', self._attr._spkmodelname)
        self._attr._btmacaddr = event.get_key('btmacaddr', self._attr._btmacaddr)
        self._attr._groupmainip = event.get_key('groupmainip', self._attr._groupmainip)
        self._attr._groupmainmacaddr = event.get_key(
            'groupmainmacaddr', self._attr._groupmainmacaddr)
        self._attr._groupspknum = event.get_key('groupspknum', self._attr._groupspknum)
        self._attr._grouptype = event.get_key('grouptype', self._attr._grouptype)
        return True

    def event_MediaBufferEndEvent(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'MediaBufferEndEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            playtime(str):
        """
        return False

    def event_MediaBufferStartEvent(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'MediaBufferStartEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            playtime(str):
        """
        return False

    def event_MultiHopInfo(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'MultiHopInfo'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            childlist(str):
            listcount(str):
            multihopcount(str):
            parentname(str):
        """
        return False

    def event_MultiQueueList(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'MultiQueueList'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            listcount(str):
            liststartindex(str):
            listtotalcount(str):
            musiclist(dict):
                music(dict | list):
                        @object_id(str):
                        album(str):
                        artist(str):
                        device_udn(str):
                        name(str):
                        playindex(str):
                        thumbnail(str):
                        timelength(str):
                        title(str):
                        type(str):
                    @object_id(str):
                    album(str):
                    artist(str):
                    device_udn(str):
                    name(str):
                    playindex(str):
                    thumbnail(str):
                    timelength(str):
                    title(str):
                    type(str):
            seqcount(str):
        """
        return False

    def event_MultichGroup(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'MultichGroup'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            audiosourcemacaddr(str, optional):
            audiosourcename(str, optional):
            audiosourcetype(str, optional):
            channeltype(str):
            channelvolume(str):
            groupindex(str):
            groupmainip(str, optional):
            groupmainmacaddr(str, optional):
            groupname(str):
            grouptype(str):
            spknum(str):
            subspklist(dict, optional):
                subspk(dict):
                    @index(str):
                    subchanneltype(str):
                    subspkip(str):
                    subspkmacaddr(str):
            subspklistcount(str, optional):
        """
        return False

    def event_MultispkGroup(self, event: 'ApiResponse') -> bool:
        """ Information about multi speaker groups.

        method (str): 'MultispkGroup'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            audiosourcemacaddr(str, optional):
                [Master]
            audiosourcename(str, optional):
                [Master]
            audiosourcetype(str, optional):
                [Master]
            groupindex(str):
                [Slave][Master] ?
            groupmainip(str, optional):
                [Slave] Master speaker IP if slave otherwise left out.
                Also received in 'MainInfo' but then the master has its own IP,
                or '0.0.0.0' if not grouped.
            groupmainmacaddr(str, optional):
                [Slave] Master speaker MAC if slave otherwise left out.
                Also received in 'MainInfo' but then the master has its own MAC,
                or '00:00:00:00:00:00' if not grouped.
            groupname(str | None):
                [Slave][Master] None for slaves?
                Also received in 'GroupName'
            grouptype(str):
                [Slave][Master] S= Slave, M= Master
            spknum(str):
                [Slave][Master] Number of speakers in the group
                Also received in 'MainInfo' but then the attribute
                is called: 'groupspknum'.
            subspklist(dict, optional):
                [Master]
                List of subspeakers. Only sent by master in the group.
                List if more than one subspeaker
                subspk(list | dict):
                        @index(str):
                            Index in list
                        subspkip(str):
                            IP of subspeaker
                        subspkmacaddr(str):
                            MAC of subspeaker
            subspklistcount(str, optional):
                [Master] Number of subspeakers
        """
        self._attr._groupmainip = event.get_key('groupmainip')
        self._attr._groupmainmacaddr = event.get_key('groupmainmacaddr')
        # Attribute spknum is called groupspknum in MainInfo so we use that instead
        self._attr._groupspknum = event.get_key('spknum')
        self._attr._grouptype = event.get_key('grouptype')
        self._attr._groupname = event.get_key('groupname')
        return True

    def event_MultispkGroupStartEvent(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'MultispkGroupStartEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            groupname(str):
            grouptype(str):
        """
        return False

    def event_MusicInfo(self, event: 'ApiResponse') -> bool:
        """ Information about what is playing.

        This is for UIC, eg DLNA.

        method (str): 'MusicInfo'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            album(str, optional):
                Album name.
            artist(str, optional):
                Artist name.
            device_udn(str, optional):
                Source device unique identifier.
            objectid(str, optional):
                ?
            parentid(str, optional):
                ?
            parentid2(str, optional):
                ?
            pause(str, optional):
                'enable' or missing.
            playbacktype(str, optional):
                'playlist' or missing.
            playertype(str, optional):
                'myphone' or missing.
            playindex(str, optional):
                Integer.
            playtime(str, optional):
                ? Duration or Position in microseconds.
            seek(str, optional):
                'enable' or missing.
            sourcename(str, optional):
                ? 'phone' or missing.
            thumbnail(str, optional):
                URL of thumbnail picture.
                NB! Can contain invalid URL eg '67.image'.
            timelength(str, optional):
                ? Seems to be total duration of playlist.
            title(str, optional):
                Song title.
        """
        # TODO: Is playbacktype=playlist an indication that next and previous is supported?
        # TODO: Is pause=enable an indication that pause is supported?

        self._attr._album = event.get_key('album', self._attr._album)
        self._attr._artist = event.get_key('artist', self._attr._artist)
        self._attr._thumbnail = event.get_key('thumbnail', self._attr._thumbnail)
        self._attr._title = event.get_key('title', self._attr._title)

        # TODO: Doesn't comply with how we do other things. This should be done in the
        # attributes module.
        timelength = str(event.get_key('timelength', '0')).replace('.', ':')
        try:
            tl = int(sum(x * int(t) for x, t in zip([3600, 60, 1, 0.001], timelength.split(":"))))
        except Exception:
            tl = 0
        self._attr._tracklength = str(tl)

        return True

    def event_MusicList(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'MusicList'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            device_udn(str):
            filter(str):
            listcount(str):
            liststartindex(str):
            listtotalcount(str):
            musiclist(dict):
                music(list):
                        @object_id(str):
                        album(str):
                        artist(str):
                        device_udn(str):
                        name(str):
                        playindex(str):
                        thumbnail(str):
                        timelength(str):
                        title(str):
                        type(str):
            parentid(str):
            parentid2(str):
            playbacktype(str):
            playertype(str):
            sourcename(str):
        """
        return False

    def event_MusicPlayTime(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'MusicPlayTime'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str): 'ok' | 'ng'
            playtime(str):
            timelength(str):
        """
        return False

    def event_MuteStatus(self, event: 'ApiResponse') -> bool:
        """ Mute state of the speaker.

        Sent when asked for (´GetMute´) or when changed (´SetMute´).

        method (str): 'MuteStatus'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID' | 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            mute(str):
                'on'|'off' - 'on' if speaker is muted.
        """
        self._attr._mute = event.get_key('mute')
        return True

    def event_PausePlaybackEvent(self, event: 'ApiResponse') -> bool:
        """ Playback paused.

        Sometimes sent when pausing playback on the speaker.

        method (str): 'PausePlaybackEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            playtime(str):
                Media position when paused.
        """
        self._attr._playstatus = 'pause'
        return True

    def event_PlayStatus(self, event: 'ApiResponse') -> bool:
        """ Play status.

        method (str): 'PlayStatus'
        type: (str): 'CPM' | 'UIC'
        version (str): '0.1' | '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            cpname(str, optional):
                'Spotify'|'Unknown'... Name of app playing
            function(str):
                Current selected source.
            playstatus(str, optional):
                'pause'|'stop'
            submode(str):
                'cp'|'dlna'
        """
        # Workaround for UrlPlayback
        # If the native app is started we need to ignore the attributes
        # if we are playing a url.
        if event.get_key('cpname') == 'Unknown' and self._attr._submode == 'url':
            return False

        self._attr._playstatus = event.get_key('playstatus', self._attr._playstatus)
        self._attr._function = event.get_key('function', self._attr._function)
        self._attr._submode = event.get_key('submode', self._attr._submode)

        cpname = event.get_key('cpname')
        if cpname != self._attr._cpname:
            self._attr.reset_media_info()
            self._attr._function = 'wifi'
            self._attr._submode = 'cp'
            self._attr._cpname = cpname

        return True

    def event_PlaybackStatus(self, event: 'ApiResponse') -> bool:
        """ Playback status.

        method (str): 'PlaybackStatus'
        type: (str): 'UIC' | 'CPM'
        version (str): '1.0' | '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID' | 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            cpname(str, optional):
                'Spotify'|'TuneIn'... Name of app playing
            function(str, optional):
                Current selected source.
                'wifi' (Only when submode = 'cp'?)
            playstatus(str):
                'play'|'pause' | 'stop' | 'resume'
            submode(str, optional):
                'cp' (Only when app is playing, not TuneIn?)
            timestamp(str, optional):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
        """
        # Workaround for UrlPlayback
        # If the native app is started we need to ignore the attributes
        # if we are playing a url.
        if event.get_key('cpname') == 'Unknown' and self._attr._submode == 'url':
            return False

        self._attr._playstatus = event.get_key('playstatus', self._attr._playstatus)
        self._attr._function = event.get_key('function', self._attr._function)
        self._attr._submode = event.get_key('submode', self._attr._submode)

        cpname = event.get_key('cpname')
        if cpname != self._attr._cpname:
            self._attr.reset_media_info()
            self._attr._function = 'wifi'
            self._attr._submode = 'cp'
            self._attr._cpname = cpname

        return True

    def event_PresetList(self, event: 'ApiResponse') -> bool:
        """ Presets stored in speaker.

        List of presets stored on the speaker.

        method (str): 'PresetList'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            cpname(str):
                Only 'TuneIn' seems to be supported?
            listcount(str):
                Number of presets requested
            presetlist(dict):
                preset(list):
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
            presetlisttype(str):
                ? '0'|'1'|'3'
            startindex(str):
                Start index of request.
            timestamp(str):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
            totallistcount(str):
                Number of presets returned.
        """
        cpname = event.get_key('cpname')
        if cpname:
            presetlist = listify(event.get_subkey('presetlist', 'preset'))
            if presetlist:
                self._attr._media_presetlist[cpname] = presetlist
                return True
        return False

    def event_QueryList(self, event: 'ApiResponse') -> bool:
        """ When searching TuneIn

        method (str): 'QueryList'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            browsemode(str):
            category(str):
            cpname(str):
            listcount(str):
            menulist(dict):
                menuitem(list):
                    @type(str):
                    contentid(str):
                    description(str, optional):
                    mediaid(str, optional):
                    thumbnail(str, optional):
                    title(str):
            root(str):
            searchquery(str):
            startindex(str):
            timestamp(str):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
            totallistcount(str):
        """
        return False

    def event_RadioInfo(self, event: 'ApiResponse') -> bool:
        """ Information about what is playing.

        This is for CPM apps. (TuneIn, Spotify ...)

        method (str): 'RadioInfo'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID' | 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            adult_yn(str, optional):
                ? ('None')
            album(str, optional):
                Name of album playing.
            allowfeedback(str, optional):
                ? ('1'|'0')
            artist(str, optional):
                Name of artist.
            cpname(str):
                Name of app playing.
                'Spotify'|'TuneIn'|'Unknown'
            description(str, optional):
                Description of the radio, can include the currently played song.
            mediaid(str, optional):
                Id on TuneIn if 'cpname' is 'TuneIn'.
            no_queue(str, optional):
                ? '1'
            playstatus(str):
                'stop'|'pause'|'play'
            presetindex(str, optional):
                Position on the preset list if 'root' is 'Favorites'.
            root(str, optional):
                ? 'Search'|'Browse'|'Favorites'
            thumbnail(str, optional):
                URL of thumbnail picture.
            timestamp(str, optional):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
            title(str, optional):
                Song title or Radio station name.
            tracklength(str, optional):
                Length of track in seconds.
        """
        # Workaround for UrlPlayback
        # If the native app is started we need to ignore the attributes
        # if we are playing a url.
        if event.get_key('cpname') == 'Unknown' and self._attr._submode == 'url':
            return False

        cpname = event.get_key('cpname')
        if cpname != self._attr._cpname:
            self._attr.reset_media_info()
            self._attr._function = 'wifi'
            self._attr._submode = 'cp'
            self._attr._cpname = cpname

        self._attr._playstatus = event.get_key('playstatus', self._attr._playstatus)
        self._attr._album = event.get_key('album', self._attr._album)
        self._attr._artist = event.get_key('artist', self._attr._artist)
        self._attr._description = event.get_key('description', self._attr._description)
        self._attr._thumbnail = event.get_key('thumbnail', self._attr._thumbnail)
        self._attr._title = event.get_key('title', self._attr._title)
        self._attr._tracklength = event.get_key('tracklength', self._attr._tracklength)

        return True

    def event_RadioList(self, event: 'ApiResponse') -> bool:
        """ When browsing TuneIn.

        method (str): 'RadioList'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            browsemode(str):
                Only seen '0'
            category(str):
                ????
            cpname(str):
                'TuneIn'
            listcount(str):
                Number of items in the list.
            menulist(dict):
                menuitem(list):
                    @cat(str, optional):
                        ????
                    @currentplaying(str, optional):
                        ???? Only seen '1'
                    @type(str):
                        Type of item
                        '0' = folder, '2' = radiostation
                    contentid(str):
                        Id to be sent to browse folder.
                    description(str, optional):
                        Description of radiostation.
                    mediaid(str, optional):
                        Id on TuneIn.
                    thumbnail(str, optional):
                        URL to radio station logo.
                    title(str):
                        Name of folder or radiostation.
            root(str):
                'Browse' | 'Search' ?
            searchquery(str, optional):
                Only when searching. Search phrase.
            startindex(str):
                Index of first item in list.
            timestamp(str):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
            totallistcount(str):
                Total items in previous and this list.
        """
        return False

    def event_RadioSelected(self, event: 'ApiResponse') -> bool:
        """ Radio (TuneIn) is selected.

        This event has no speaker state attributes!

        TuneIn selected for doing operations, and not what is playing on
        the speaker. You could have 'Spotify' selected and at the same
        time playing a TuneIn radio channel, or vice versa.

        method (str): 'RadioSelected'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            audioinfo(dict, optional):
                playstatus(str):
                    ? 'stop'
                thumbnail(str):
                    Thumbnail to stations logo/picture
                title(str):
                    Title of current selected station.
            cpname(str):
                'TuneIn'
            signinstatus(str):
                '0'|'1' - 1 if signed in to TuneIn.
            timestamp(str):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
            username(str, optional):
                Username that is signed in.
        """
        return False

    def event_RepeatMode(self, event: 'ApiResponse') -> bool:
        """ Repeat mode.

        method (str): 'RepeatMode'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            repeat(str):
                'one'|'all'|'off' for repeat one track, all tracks
                on the playlist, or disabled repeat mode.
        """
        self._attr._repeat = event.get_key('repeat')
        return True

    def event_RequestDeviceInfo(self, event: 'ApiResponse') -> bool:
        """ Empty message.

        Sent as first repsonse to API call ´GetMainInfo´.

        method (str): 'RequestDeviceInfo'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (str):
        """
        return False

    def event_Reset7bandEQValue(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'Reset7bandEQValue'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            eqvalue1(str):
            eqvalue2(str):
            eqvalue3(str):
            eqvalue4(str):
            eqvalue5(str):
            eqvalue6(str):
            eqvalue7(str):
            presetindex(str):
        """
        return False

    def event_SavePreset(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'SavePreset'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            cpname(str):
            description(str):
            thumbnail(str):
            timestamp(str):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
            title(str):
        """
        return False

    def event_SelectCpService(self, event: 'ApiResponse') -> bool:
        """ Selected cp service.

        - Seems to be emitted when apps other than TuneIn is selected
          for browsing. Has nothing to do with what is playing.
        - Sent when Spotify is playing but then changed to another
          speaker from the Spotify app.

        method (str): 'SelectCpService'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID' | 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            category(str, optional):
                ?
            cpname(str):
                Name of app selected.
            signinstatus(str):
                '0'|'1' - '1' if signed in
            timestamp(str, optional):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
        """
        if event.get_key('cpname') == self._attr._cpname:
            if event.get_key('signinstatus') == '0':
                self._attr.reset_media_info()
            return True
        return False

    def event_ShuffleMode(self, event: 'ApiResponse') -> bool:
        """ Shuffle mode.

        method (str): 'ShuffleMode'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            shuffle(str):
                'on'|'off'
        """
        self._attr._shuffle = event.get_key('shuffle')
        return True

    def event_SleepTime(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'SleepTime'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            sleepoption(str):
            sleeptime(str):
        """
        return False

    def event_SoftwareVersion(self, event: 'ApiResponse') -> bool:
        """ Firmware version on speaker.

        method (str): 'SoftwareVersion'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            displayversion(str):
                Version of firmware
            version(str):
                Version of firmware
        """
        self._attr._displayversion = event.get_key('displayversion')
        return True

    def event_SpeakerBuyer(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'SpeakerBuyer'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            buyer(str):
        """
        return False

    def event_SpeakerTime(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'SpeakerTime'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            day(str):
            hour(str):
            min(str):
            month(str):
            sec(str):
            year(str):
        """
        return False

    def event_SpeakerWifiRegion(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'SpeakerWifiRegion'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            wifi(str):
        """
        return False

    def event_SpkName(self, event: 'ApiResponse') -> bool:
        """ Speaker name.

        Sent when speaker name is asked for (´GetSpkName´)
        or changed (´SetSpkName´).

        method (str): 'SpkName'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str):
                'ok' | 'ng'
            spkname(str):
                Name of the speaker
        """
        self._attr._spkname = event.get_key('spkname')
        return True

    def event_StartPlaybackEvent(self, event: 'ApiResponse') -> bool:
        """ Start playback.

        Sent when starting playback on the speaker.

        method (str): 'StartPlaybackEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            playtime(str):
                ?
        """
        self._attr._playstatus = 'play'
        return True

    def event_StationData(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'StationData'
        type: (str): 'CPM'
        version (str): '0.1'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            browsemode(str):
            cpname(str):
            description(str):
            stationurl(str):
            thumbnail(str):
            timestamp(str):
                UTC ISO 8601 format (eg '2020-02-19T17:26:24Z')
            title(str):
        """
        return False

    def event_StopPlaybackEvent(self, event: 'ApiResponse') -> bool:
        """ Stop playback.

        Sometimes sent when stopping playback on the speaker.

        method (str): 'StopPlaybackEvent'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            playtime(str):
                ?
        """
        self._attr._playstatus = 'stop'
        return True

    def event_SubSoftwareVersion(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'SubSoftwareVersion'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            Subversion1(str):
            Subversion2(str):
            Subversion3(str):
            Subversion4(str):
            Subversion5(str):
        """
        return False

    def event_Ungroup(self, event: 'ApiResponse') -> bool:
        """ Speaker is ungrouped.

        Sent when a a group is cancelled.

        method (str): 'Ungroup'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
        """
        self._attr._groupmainip = '0.0.0.0'
        self._attr._groupmainmacaddr = '00:00:00:00:00:00'
        self._attr._groupspknum = '1'
        self._attr._grouptype = 'N'
        self._attr._groupname = ''

        return True

    def event_UniversalSearchMusicList(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'UniversalSearchMusicList'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            category(str):
            device_udn(str):
            filter(str):
            listcount(str):
            liststartindex(str):
            listtotalcount(str):
            musiclist(str | dict):
                music(list | dict):
                        @object_id(str):
                        album(str):
                        artist(str):
                        device_udn(str):
                        name(str):
                        playindex(str):
                        thumbnail(str):
                        timelength(str):
                        title(str):
                        type(str):
                    @object_id(str):
                    album(str):
                    artist(str):
                    device_udn(str):
                    name(str):
                    playindex(str):
                    thumbnail(str):
                    timelength(str):
                    title(str):
                    type(str):
            parentid(str):
            parentid2(str):
            playbacktype(str):
            playertype(str):
            query(str):
            sourcename(str):
            timestamp(str):
                NB! Unix time (eg '1585081896274')
        """
        return False

    def event_UrlPlayback(self, event: 'ApiResponse') -> bool:
        """ Url playing.

        method (str): 'UrlPlayback'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'None'

        response (dict):
            @result (str):
                'ok' | 'ng'
            buffersize (str):
                ?
            seektime (str):
                ?
        """
        self._attr.reset_source_info()
        self._attr.reset_media_info()
        self._attr._function = 'wifi'
        self._attr._submode = 'url'
        self._attr._playstatus = 'play'
        self._attr._cpname = 'Unknown'
        return True

    def event_ValidAppVersion(self, event: 'ApiResponse') -> bool:
        """ ????.

        method (str): 'ValidAppVersion'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'UUID'

        response (dict):
            @result(str): 'ok' | 'ng'
            android(str):
            ios(str):
        """
        return False

    def event_VolumeLevel(self, event: 'ApiResponse') -> bool:
        """ Speaker volume level.

        Sent when asked (´GetVolume´) for or
        when volume is changed (´SetVolume´).

        method (str): 'VolumeLevel'
        type: (str): 'UIC'
        version (str): '1.0'
        speakerip (str): Speakers IP-address.
        user_identifier (str): 'None' | 'UUID' | 'public'

        response (dict):
            @result(str):
                'ok' | 'ng'
            volume(str):
                Speaker volume between 0 and 30.
        """
        self._attr._volume = event.get_key('volume')
        return True
