# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Classes and function for handling the equalizer. """
from __future__ import annotations


class EqualizerPreset:
    """ Stored equalizer presets on the speaker. """

    def __init__(self, presetindex: str, presetname: str, **kwargs) -> None:
        self._presetindex = presetindex
        self._presetname = presetname

    @property
    def name(self) -> str:
        """ Return name of preset. """
        return self._presetname

    @property
    def index(self) -> int:
        """ Return index of preset. """
        return int(self._presetindex)


class EqualizerValues:
    """ Equalizer values.

    Attributes:
        hz_150:
            150 Hz, value between -6 and 6.
        hz_300:
            300 Hz, value between -6 and 6.
        hz_600:
            600 Hz, value between -6 and 6.
        hz_1200:
            1.2 kHz, value between -6 and 6.
        hz_2500:
            2.5 kHz, value between -6 and 6.
        hz_5000:
            5.0 kHz, value between -6 and 6.
        hz_10000:
            10 kHz, value between -6 and 6.
    """

    def __init__(self,
                 hz_150: str,
                 hz_300: str,
                 hz_600: str,
                 hz_1200: str,
                 hz_2500: str,
                 hz_5000: str,
                 hz_10000: str) -> None:
        self._hz_150 = hz_150
        self._hz_300 = hz_300
        self._hz_600 = hz_600
        self._hz_1200 = hz_1200
        self._hz_2500 = hz_2500
        self._hz_5000 = hz_5000
        self._hz_10000 = hz_10000

    @property
    def hz_150(self) -> int:
        """" Return 150 Hz eq setting, value between -6 and 6."""
        return int(self._hz_150)

    @property
    def hz_300(self) -> int:
        """" Return 300 Hz eq setting, value between -6 and 6."""
        return int(self._hz_300)

    @property
    def hz_600(self) -> int:
        """" Return 600 Hz eq setting, value between -6 and 6."""
        return int(self._hz_600)

    @property
    def hz_1200(self) -> int:
        """" Return 1.2 kHz eq setting, value between -6 and 6."""
        return int(self._hz_1200)

    @property
    def hz_2500(self) -> int:
        """" Return 2.5 kHz eq setting, value between -6 and 6."""
        return int(self._hz_2500)

    @property
    def hz_5000(self) -> int:
        """" Return 5.0 kHz eq setting, value between -6 and 6."""
        return int(self._hz_5000)

    @property
    def hz_10000(self) -> int:
        """" Return 10 kHz eq setting, value between -6 and 6."""
        return int(self._hz_10000)

    @property
    def values(self) -> list[int]:
        """ Return all values in a list. """
        return [self.hz_150,
                self.hz_300,
                self.hz_600,
                self.hz_1200,
                self.hz_2500,
                self.hz_5000,
                self.hz_10000,
                ]
