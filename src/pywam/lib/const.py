# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Constants.

Project constants that stores information that we can't get from the
speaker.
"""


class Feature:
    """ Supported features. """
    NEXT = 'cmd_next'
    PAUSE = 'cmd_pause'
    PLAY = 'cmd_play'
    PREV = 'cmd_previous'
    STOP = 'cmd_stop'
    PLAY_PRESET = 'play_preset'
    PLAY_BROWSER_ITEM = 'play_browser_item'
    PLAY_URL = 'play_url'
    SET_NAME = 'set_name'
    SET_REPEAT = 'set_repeat_mode'
    SET_SHUFFLE = 'set_shuffle'
    SELECT_SOURCE = 'select_source'


EXC_MESSAGE: dict[str, str] = {
    'cmd_next': 'Next',
    'cmd_pause': 'Pause',
    'cmd_play': 'Play',
    'cmd_previous': 'Previous',
    'cmd_stop': 'Stop',
    'play_preset': 'Playing presets',
    'play_browser_item': 'Playing browser items',
    'play_url': 'Playing a URL',
    'set_name': 'Changing speaker name',
    'set_repeat_mode': 'Repeat mode',
    'set_shuffle': 'Shuffle mode',
    'select_source': 'Selecting source',
}

APP_FEATURES: dict[str, list[str]] = {
    'Pandora': [Feature.STOP, Feature.PLAY],
    'Spotify': [Feature.PLAY],
    'Deezer': [Feature.STOP, Feature.PLAY],
    'Napster': [Feature.STOP, Feature.PLAY],
    '8tracks': [Feature.STOP, Feature.PLAY],
    'iHeartRadio': [Feature.STOP, Feature.PLAY],
    'Rdio': [Feature.STOP, Feature.PLAY],
    'BugsMusic': [Feature.STOP, Feature.PLAY],
    'JUKE': [Feature.STOP, Feature.PLAY],
    '7digital': [Feature.STOP, Feature.PLAY],
    'Murfie': [Feature.STOP, Feature.PLAY],
    'JB HI-FI Now': [Feature.STOP, Feature.PLAY],
    'Rhapsody': [Feature.STOP, Feature.PLAY],
    'Qobuz': [Feature.STOP, Feature.PLAY],
    'Stitcher': [Feature.STOP, Feature.PLAY],
    'MTV Music': [Feature.STOP, Feature.PLAY],
    'Milk Music': [Feature.STOP, Feature.PLAY],
    'Milk Music Radio': [Feature.STOP, Feature.PLAY],
    'MelOn': [Feature.STOP, Feature.PLAY],
    'Tidal HiFi': [Feature.STOP, Feature.PLAY],
    'SiriusXM': [Feature.STOP, Feature.PLAY],
    'Anghami': [Feature.STOP, Feature.PLAY],
    'AmazonPrime': [Feature.STOP, Feature.PLAY],
    'Amazon': [Feature.STOP, Feature.PLAY],
    'TuneIn': [Feature.PLAY],
    'Unknown': [Feature.STOP],
    'DLNA': [Feature.PLAY, Feature.PREV,
             Feature.NEXT, Feature.SET_SHUFFLE, Feature.SET_REPEAT],
    'URL Playback': [],
}

SOURCE_FEATURES: dict[str, list[str]] = {
    'AUX': [],
    'Bluetooth': [],
    'Coaxial': [],
    'HDMI': [],
    'HDMI 1': [],
    'HDMI 2': [],
    'Optical': [],
    'TV SoundConnect': [],
    'USB': [],
    'Wi-Fi': [Feature.PLAY_URL, Feature.PLAY_PRESET],
}

SOURCES_BY_NAME: dict[str, str] = {
    'AUX': 'aux',
    'Bluetooth': 'bt',
    'Coaxial': 'coaxial',
    'HDMI': 'hdmi',
    'HDMI 1': 'hdmi1',
    'HDMI 2': 'hdmi2',
    'Optical': 'optical',
    'TV SoundConnect': 'soundshare',
    'USB': 'usb',
    'Wi-Fi': 'wifi',
}
SOURCES_BY_API = {value: key for key, value in SOURCES_BY_NAME.items()}
