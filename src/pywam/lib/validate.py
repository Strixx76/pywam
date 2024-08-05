# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Functions for validating user inputs. """
from __future__ import annotations

import ipaddress
from typing import TYPE_CHECKING
import uuid

from pywam.lib.const import SPEAKER_MODELS
from pywam.lib.equalizer import EqualizerPreset, EqualizerValues
from pywam.lib.media_presets import MediaPreset
from pywam.lib.url import UrlMediaItem

if TYPE_CHECKING:
    from pywam.speaker import Speaker


def speakers(speakers: list[Speaker]) -> list[Speaker]:
    """ Validate a speaker objects.

    Checks that the speaker object has both IP and MAC so that we can use it
    for grouping speakers.

    Arguments:
        speakers:
            List of Speaker objects to validate.
    Returns:
        Validated value.

    Raises:
        TypeError:
            If not an list of Speaker object.
        ValueError:
            If Speaker has no IP or MAC attribute.
    """
    if not isinstance(speakers, list):
        raise TypeError('Speaker must be a list of Speaker object')

    from pywam.speaker import Speaker  # To avoid circular imports
    for speaker in speakers:
        if not isinstance(speaker, Speaker):
            raise TypeError('Speaker must be a Speaker object')
        if not speaker.ip:
            raise ValueError('Speaker has no IP address')
        if not speaker.attribute.mac:
            raise ValueError('Speaker has no MAC address')

    return speakers


def equalizer_preset(preset: EqualizerPreset,
                     preset_list: list[EqualizerPreset],
                     ) -> EqualizerPreset:
    """ Validate equalizer preset.

    Arguments:
        preset:
            EqualizerPreset object to validate.
        preset_list:
            List of presets on the speaker.

    Returns:
        Validated EqualizerPreset.

    Raises:
        TypeError:
            If not an EqualizerPreset object.
        ValueError:
            If preset is not found on the speaker.
    """
    if not preset_list:
        raise ValueError('Can not find any presets on the speaker')
    if not isinstance(preset, EqualizerPreset):
        raise TypeError('Preset must be a EqualizerPreset object')
    for in_list in preset_list:
        if preset.name == in_list.name:
            if preset.index == in_list.index:
                return preset

    raise ValueError('Preset could not be found on the speaker')


def equalizer_values(values: EqualizerValues) -> EqualizerValues:
    """ Validate equalizer values.

    Arguments:
        values:
            EqualizerValues object to validate.

    Returns:
        Validated EqualizerValues.

    Raises:
        TypeError:
            If not an EqualizerValues object or values is not integers.
        ValueError:
            If value is not within range if given.
    """
    if not isinstance(values, EqualizerValues):
        raise TypeError('Preset must be a EqualizerValues object')

    for value in values.values:
        if not isinstance(value, int):
            raise TypeError('Equalizer band value must be a integer')
        if not -6 <= value <= 6:
            raise ValueError('Equalizer band value must be between -6 and 6')

    return values


def is_boolean(val: bool) -> bool:
    """ Is value an boolean.

    Arguments:
        val:
            Value to validate.

    Returns:
        Validated value.

    Raises:
        TypeError:
            If value is not a boolean.
    """
    if not isinstance(val, bool):
        raise TypeError('Value must be a boolean')
    return val


def is_integer(val: int, in_range: tuple[int, int] | None = None) -> int:
    """ Is value an integer.

    Arguments:
        val:
            Value to validate.
        in_range (optional):
            If given the integer should not be less than in_range[0]
            and not greater than in_range[1].

    Returns:
        Validated value.

    Raises:
        TypeError:
            If value is not a integer.
        ValueError:
            If value is not within range if given.
    """
    if not isinstance(val, int):
        raise TypeError('Value must be a integer')
    if in_range:
        if not in_range[0] <= val <= in_range[1]:
            raise ValueError(
                f'Value must be between {in_range[0]} and {in_range[1]}'
            )
    return val


def ip(ip: str) -> str:
    """ Validate IP address.

    Arguments:
        ip:
            IP address to validate.

    Returns:
        IP address.

    Raises:
        TypeError:
            If IP address is not a valid.
        ValueError:
            If IP address is not private.
    """
    if not isinstance(ip, str):
        raise TypeError('Speaker IP must be a string')
    try:
        test_ip = ipaddress.ip_address(ip)
    except Exception:
        raise TypeError('Speaker IP is not a valid IP address')
    if not test_ip.is_private:
        raise ValueError('Speaker IP is not a private IP address')
    return ip


def name(name: str) -> str:
    """ Validate speaker name.

    Arguments:
        name:
            Name.

    Returns:
        Name.

    Raises:
        TypeError:
            If name is not a string.
        ValueError:
            If name is not valid.
    """
    if not isinstance(name, str):
        raise TypeError('Speaker name must be a string')
    if not name.isprintable():
        raise ValueError('Speaker name contains unprintable characters')
    if len(name) > 64:
        raise ValueError('Speaker name to long')
    if len(name) < 1:
        raise ValueError('Speaker name to short')
    return name


def port(port: int) -> int:
    """ Validate TCP port.

    Arguments:
        port: TCP port to validate.

    Returns:
        TCP port.

    Raises:
        TypeError:
            If TCP port is not a integer.
        ValueError:
            IF TCP port is out of range.
    """
    if not isinstance(port, int):
        raise TypeError('Speaker port must be a integer')
    if not 0 < port < 65536:
        raise ValueError('Speaker port is not valid port number')
    return port


def media_preset(preset: MediaPreset, preset_list: list[MediaPreset]) -> MediaPreset:
    """ Validate a media preset.

    Arguments:
        preset:
            Preset to be played.
        preset_list:
            List of presets on the speaker.

    Returns:
        Validated preset.

    Raises:
        TypeError:
            If not an EqualizerPreset object.
        ValueError:
            If preset is not found on the speaker.
    """
    if not preset_list:
        raise ValueError('Can not find any presets on the speaker')
    if not isinstance(preset, MediaPreset):
        raise TypeError('Preset must be a MediaPreset object')
    for in_list in preset_list:
        if preset.title == in_list.title:
            if preset.contentid == in_list.contentid:
                return preset

    raise ValueError('Preset could not be found on the speaker')


def source(source: str, model: str | None) -> str:
    """ Validate source.

    Arguments:
        source:
            Source to validate
        model:
            Speaker model as WAM string

    Returns:
        Validated source.

    Raises:
        TypeError:
            If source is not a string.
        ValueError:
            If given source is not correct.
    """
    if not isinstance(source, str):
        raise TypeError('Source must be a string')
    if not isinstance(model, str):
        raise ValueError('Could not find speaker model')
    if model not in SPEAKER_MODELS:
        model = 'UNRECOGNIZED'
    sources = SPEAKER_MODELS[model]['sources']
    if source not in sources:
        raise ValueError('Could not find selected source')
    return source


def url_media_item(item: UrlMediaItem) -> UrlMediaItem:
    """ Validate url media items.

    Arguments:
        item:
            UrlMediaItem to validate.

    Returns:
        Validated value.

    Raises:
        TypeError:
            If not a UrlMediaItem object.
    """
    if not isinstance(item, UrlMediaItem):
        raise TypeError('Must be a UrlMediaItem object.')
    return item


def user(user: str) -> str:
    """ Validate UUID.

    If a empty string is given as argument, a new UUID will be returned.

    Arguments:
        user:
            UUID to validate or empty string.

    Returns:
        UUID.

    Raises:
        TypeError:
            If UUID is not a string.
        ValueError:
            If UUID is not a valid UUID
    """
    if not isinstance(user, str):
        raise TypeError('User must be a string')
    if not user:
        return str(uuid.uuid1())
    try:
        val_user = uuid.UUID(user)
    except Exception:
        raise ValueError('Given UUID is not valid')
    return str(val_user)


def volume(volume: int) -> int:
    """ Validate speaker volume.

    Arguments:
        volume:
            Volume.

    Returns:
        Volume

    Raises:
        TypeError:
            If volume is not a integer.
        ValueError:
            If volume is out of range.
    """
    if not isinstance(volume, int):
        raise TypeError("Volume must be an integer")
    if not 0 <= volume <= 100:
        raise ValueError("Volume must be between 0 and 100")
    return volume
