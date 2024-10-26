# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Constants.

Project constants that stores information that we can't get from the
speaker.
"""

from typing import Any


class Feature():
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
    'HDMI': [],
    'HDMI 1': [],
    'HDMI 2': [],
    'Optical': [],
    'TV SoundConnect': [],
    'Wi-Fi': [Feature.PLAY_URL, Feature.PLAY_PRESET],
    'USB': [],
}

SOURCES_BY_NAME: dict[str, str] = {
    'AUX': 'aux',
    'Bluetooth': 'bt',
    'HDMI': 'hdmi',
    'HDMI 1': 'hdmi1',
    'HDMI 2': 'hdmi2',
    'Optical': 'optical',
    'TV SoundConnect': 'soundshare',
    'Wi-Fi': 'wifi',
    'USB': 'usb',
}

SPEAKER_MODELS: dict[str, dict[str, Any]] = {
    'SPK-WAM350': {'name': 'Shape M3',
                   'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                   'max_api_volume': 30,
                   'port': 55001,
                   },
    'SPK-WAM351': {'name': 'Shape M3',
                   'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                   'max_api_volume': 30,
                   'port': 55001,
                   },
    'SPK-WAM550': {'name': 'Shape M5',
                   'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                   'max_api_volume': 30,
                   'port': 55001,
                   },
    'SPK-WAM551': {'name': 'Shape M5',
                   'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                   'max_api_volume': 30,
                   'port': 55001,
                   },
    'SPK-WAM750': {'name': 'Shape M7',
                   'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'TV SoundConnect'],
                   'max_api_volume': 30,
                   'port': 55001,
                   },
    'SPK-WAM751': {'name': 'Shape M7',
                   'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'TV SoundConnect'],
                   'max_api_volume': 30,
                   'port': 55001,
                   },
    'SPK-WAM1400': {'name': 'Wireless Audio 360 - R1 Lite',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM1401': {'name': 'Wireless Audio 360 - R1 Lite',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM1500': {'name': 'Wireless Audio 360 - R1',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM1501': {'name': 'Wireless Audio 360 - R1',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM3500': {'name': 'Wireless Audio 360 - R3',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM3501': {'name': 'Wireless Audio 360 - R3',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM5500': {'name': 'Wireless Audio 360 - R5',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM5501': {'name': 'Wireless Audio 360 - R5',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM6500': {'name': 'Wireless Audio 360 - R6',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM6501': {'name': 'Wireless Audio 360 - R6',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM7500': {'name': 'Wireless Audio 360 - R7',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    'SPK-WAM7501': {'name': 'Wireless Audio 360 - R7',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    'max_api_volume': 30,
                    'port': 55001,
                    },
    # Following speakers are not tested.
    'WAM270': {'name': 'Multiroom Link Mate',
               'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                           'TV SoundConnect'],
               'max_api_volume': 30,
               'port': 55001,
               },
    'HW-H750': {'name': '4.1 Ch Soundbar H750',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect', 'USB'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-J650': {'name': 'Wireless Smart Soundbar with HD Audio',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect', 'USB'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-J651': {'name': 'Wireless Smart Soundbar with HD Audio',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-J660': {'name': '4.1 Ch Soundbar J660',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-J6510R': {'name': '2.1 Ch Curved Soundbar J6510R',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                              'TV SoundConnect'],
                  'max_api_volume': 30,
                  'port': 55001,
                  },
    'HW-J6512': {'name': '6.1 Ch Curved Soundbar J6512',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-J7500': {'name': '55" Curved Wireless Soundbar',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect', 'USB'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-J7510': {'name': '8.1 Ch Soundbar J7510',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-J7511R': {'name': '4.1 Ch Curved Soundbar J7511R',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                              'TV SoundConnect'],
                  'max_api_volume': 30,
                  'port': 55001,
                  },
    'HW-J8500': {'name': '65" Curved Wireless Soundbar',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect', 'USB'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-J8510': {'name': '9.1 Ch Curved Soundbar J8510',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-J8511R': {'name': '5.1 Ch Curved Soundbar J8511R',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                              'TV SoundConnect'],
                  'max_api_volume': 30,
                  'port': 55001,
                  },
    'HW-K650': {'name': 'K650 Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect', 'USB'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-K860': {'name': 'Cinematic Soundbar K8',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-K950': {'name': 'Cinematic Soundbar K9',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-K960': {'name': 'Cinematic Soundbar K9',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-MS560': {'name': 'All-in-One Flat Soundbar Sound+ MS5',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-MS650': {'name': 'Sound+ HW-MS650',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-MS660': {'name': 'All-in-One Flat Soundbar Sound+ MS6',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-MS661': {'name': 'All-in-One Flat Soundbar Sound+ MS6',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-MS750': {'name': 'Sound+ HW-MS750 Smart Soundbar',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                             'Optical', 'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-MS760': {'name': 'All-in-One Flat Soundbar Sound+ MS7',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                             'Optical', 'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-MS761': {'name': 'All-in-One Flat Soundbar Sound+ MS7',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                             'Optical', 'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-MS6500': {'name': 'Sound+ HW-MS6500 Wireless Curved Smart Soundbar',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                              'TV SoundConnect'],
                  'max_api_volume': 30,
                  'port': 55001,
                  },
    'HW-MS6510': {'name': 'All-in-One Curved Soundbar Sound+ MS6',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX',  'HDMI', 'Optical',
                              'TV SoundConnect'],
                  'max_api_volume': 30,
                  'port': 55001,
                  },
    'HW-MS7500': {'name': 'HW-J7500R Curved Soundbar',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                              'Optical', 'TV SoundConnect'],
                  'max_api_volume': 30,
                  'port': 55001,
                  },
    'HW-N400': {'name': 'HW-N400 All in One Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-N850': {'name': 'HW-N850 Samsung Harman/Kardon Soundbar with Dolby Atmos',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-N960': {'name': '7.1.4ch Cinematic Soundbar N9',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-Q70R': {'name': 'HW-Q70R Samsung Harman Kardon Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-Q76R': {'name': 'HW-Q76R Dolby Atmos Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-Q80R': {'name': 'HW-Q80R Samsung Harman Kardon 5.1.2ch Soundbar with Dolby Atmos',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-Q86R': {'name': 'HW-Q86R 5.1.2ch Dolby Atmos Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-Q90R': {'name': 'HW-Q90R Samsung Harman Kardon 7.1.4ch Soundbar with Dolby Atmos',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-Q96R': {'name': 'HW-Q96R 7.1.4ch Dolby Atmos Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'HW-Q800T': {'name': 'HW-Q800T Dolby Atmos Soundbar',
                 'sources': ['Bluetooth', 'Wi-Fi', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 'max_api_volume': 30,
                 'port': 55001,
                 },
    'HW-R550': {'name': 'HW-R550 Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                'max_api_volume': 30,
                'port': 55001,
                },
    'UNRECOGNIZED': {'name': 'Unknown model',
                     'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                     'max_api_volume': 30,
                     'port': 55001,
                     }
}
