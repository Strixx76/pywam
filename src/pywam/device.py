# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Samsung Wireless Audio device.

Information about the device that is not available in the API.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SPEAKER_MODELS: dict[str, dict[str, Any]] = {
    # Confirmed working
    'SPK-WAM350': {'name': 'Shape M3',
                   'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                   },
    'SPK-WAM351': {'name': 'Shape M3',
                   'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                   },
    'SPK-WAM550': {'name': 'Shape M5',
                   'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                   },
    'SPK-WAM551': {'name': 'Shape M5',
                   'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                   },
    'SPK-WAM750': {'name': 'Shape M7',
                   'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'TV SoundConnect'],
                   'master_sources': ['Wi-Fi', 'AUX'],
                   },
    'SPK-WAM751': {'name': 'Shape M7',
                   'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'TV SoundConnect'],
                   'master_sources': ['Wi-Fi', 'AUX'],
                   },
    'SPK-WAM1400': {'name': 'Wireless Audio 360 - R1 Lite',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM1401': {'name': 'Wireless Audio 360 - R1 Lite',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM1500': {'name': 'Wireless Audio 360 - R1',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM1501': {'name': 'Wireless Audio 360 - R1',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM3500': {'name': 'Wireless Audio 360 - R3',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM3501': {'name': 'Wireless Audio 360 - R3',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM5500': {'name': 'Wireless Audio 360 - R5',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM5501': {'name': 'Wireless Audio 360 - R5',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM6500': {'name': 'Wireless Audio 360 - R6',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM6501': {'name': 'Wireless Audio 360 - R6',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM7500': {'name': 'Wireless Audio 360 - R7',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    'SPK-WAM7501': {'name': 'Wireless Audio 360 - R7',
                    'sources': ['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                    },
    # Testing
    'SPK-WAM270': {'name': 'Multi room Link Mate',
                   'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'Optical',
                               'Coaxial', 'TV SoundConnect'],
                   'master_sources': ['Wi-Fi', 'AUX', 'Optical', 'Coaxial'],
                   },
    # Not tested or confirmed.
    'HW-H750': {'name': '4.1 Ch Soundbar H750',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect', 'USB'],
                },
    'HW-J650': {'name': 'Wireless Smart Soundbar with HD Audio',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect', 'USB'],
                },
    'HW-J651': {'name': 'Wireless Smart Soundbar with HD Audio',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                },
    'HW-J660': {'name': '4.1 Ch Soundbar J660',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                },
    'HW-J6510R': {'name': '2.1 Ch Curved Soundbar J6510R',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                              'TV SoundConnect'],
                  },
    'HW-J6512': {'name': '6.1 Ch Curved Soundbar J6512',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 },
    'HW-J7500': {'name': '55" Curved Wireless Soundbar',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect', 'USB'],
                 },
    'HW-J7510': {'name': '8.1 Ch Soundbar J7510',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 },
    'HW-J7511R': {'name': '4.1 Ch Curved Soundbar J7511R',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                              'TV SoundConnect'],
                  },
    'HW-J8500': {'name': '65" Curved Wireless Soundbar',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect', 'USB'],
                 },
    'HW-J8510': {'name': '9.1 Ch Curved Soundbar J8510',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 },
    'HW-J8511R': {'name': '5.1 Ch Curved Soundbar J8511R',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                              'TV SoundConnect'],
                  },
    'HW-K650': {'name': 'K650 Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect', 'USB'],
                },
    'HW-K860': {'name': 'Cinematic Soundbar K8',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                },
    'HW-K950': {'name': 'Cinematic Soundbar K9',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                },
    'HW-K960': {'name': 'Cinematic Soundbar K9',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                },
    'HW-MS560': {'name': 'All-in-One Flat Soundbar Sound+ MS5',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 },
    'HW-MS650': {'name': 'Sound+ HW-MS650',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 },
    'HW-MS660': {'name': 'All-in-One Flat Soundbar Sound+ MS6',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 },
    'HW-MS661': {'name': 'All-in-One Flat Soundbar Sound+ MS6',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 },
    'HW-MS750': {'name': 'Sound+ HW-MS750 Smart Soundbar',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                             'Optical', 'TV SoundConnect'],
                 },
    'HW-MS760': {'name': 'All-in-One Flat Soundbar Sound+ MS7',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                             'Optical', 'TV SoundConnect'],
                 },
    'HW-MS761': {'name': 'All-in-One Flat Soundbar Sound+ MS7',
                 'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                             'Optical', 'TV SoundConnect'],
                 },
    'HW-MS6500': {'name': 'Sound+ HW-MS6500 Wireless Curved Smart Soundbar',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                              'TV SoundConnect'],
                  },
    'HW-MS6510': {'name': 'All-in-One Curved Soundbar Sound+ MS6',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX',  'HDMI', 'Optical',
                              'TV SoundConnect'],
                  },
    'HW-MS7500': {'name': 'HW-J7500R Curved Soundbar',
                  'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI 1', 'HDMI 2',
                              'Optical', 'TV SoundConnect'],
                  },
    'HW-N400': {'name': 'HW-N400 All in One Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'AUX', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                },
    'HW-N850': {'name': 'HW-N850 Samsung Harman/Kardon Soundbar with Dolby Atmos',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                },
    'HW-N960': {'name': '7.1.4ch Cinematic Soundbar N9',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                },
    'HW-Q70R': {'name': 'HW-Q70R Samsung Harman Kardon Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                },
    'HW-Q76R': {'name': 'HW-Q76R Dolby Atmos Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                },
    'HW-Q80R': {'name': 'HW-Q80R Samsung Harman Kardon 5.1.2ch Soundbar with Dolby Atmos',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                },
    'HW-Q86R': {'name': 'HW-Q86R 5.1.2ch Dolby Atmos Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                },
    'HW-Q90R': {'name': 'HW-Q90R Samsung Harman Kardon 7.1.4ch Soundbar with Dolby Atmos',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                },
    'HW-Q96R': {'name': 'HW-Q96R 7.1.4ch Dolby Atmos Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI 1', 'HDMI 2',
                            'Optical', 'TV SoundConnect'],
                },
    'HW-Q800T': {'name': 'HW-Q800T Dolby Atmos Soundbar',
                 'sources': ['Bluetooth', 'Wi-Fi', 'HDMI', 'Optical',
                             'TV SoundConnect'],
                 },
    'HW-R550': {'name': 'HW-R550 Soundbar',
                'sources': ['Bluetooth', 'Wi-Fi', 'HDMI', 'Optical',
                            'TV SoundConnect'],
                },
}


def get_device_info(device: str | None = None) -> DeviceInfo:
    """ Retrieve device info.

    Arguments:
        device:
            Model according to API response.

    Returns:
        DeviceInfo:
            Device info.
    """
    if device is None or device not in SPEAKER_MODELS:
        return DeviceInfo(name='Unknown model',
                          sources=['Bluetooth', 'Wi-Fi', 'TV SoundConnect'],
                          )

    return DeviceInfo(**SPEAKER_MODELS[device])


@ dataclass
class DeviceInfo:
    """ Stores info about a device. """
    name: str
    sources: list[str]
    master_sources: list[str] = field(default_factory=lambda: ['Wi-Fi'])
    max_api_volume: int = 30
    port: int = 55001


class WamDevice:
    """ Samsung Wireless Audio device. """

    def __init__(self):
        """ Initialize the device with the given model. """
        self._device_info = get_device_info()

    @ property
    def model(self) -> str:
        """ Return speaker model name. """
        return self._device_info.name

    @property
    def sources(self) -> list[str]:
        """ Return available sources. """
        return self._device_info.sources

    @property
    def master_sources(self) -> list[str]:
        """ Return available master sources. """
        return self._device_info.master_sources

    def update_model(self, model: str | None) -> None:
        """ Update the device model """
        self._device_info = get_device_info(model)

    def encode_volume(self, volume: int) -> int:
        """ Translate volume to API values. """
        factor = self._device_info.max_api_volume / 100
        vol = int(volume * factor)
        return min(max(vol, 0), self._device_info.max_api_volume)

    def decode_volume(self, volume: int) -> int:
        """ Translate volume to user value. """
        factor = 100 / self._device_info.max_api_volume
        vol = int(volume * factor)
        return min(max(vol, 0), 100)
