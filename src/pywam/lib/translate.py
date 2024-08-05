# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Translate and store translated WAM API values.

This module should be initialized once with the :init(): function.
"""
from __future__ import annotations

from typing import Any

from pywam.lib.const import SOURCES_BY_NAME, SPEAKER_MODELS
from pywam.lib.exceptions import PywamError

# First time?
_init: bool = False
# Model
_model_info: dict[str, Any] = SPEAKER_MODELS['UNRECOGNIZED']
# Model name
_model_name: str = _model_info['name']
# Volume
_max_api_volume: int = _model_info['max_api_volume']
_vol_to_api: float = _max_api_volume / 100
_vol_to_user: float = 100 / _max_api_volume
# Sources
_sources: list[str] = _model_info['sources']
_source_to_api = SOURCES_BY_NAME
_source_to_user = {value: key for key, value in SOURCES_BY_NAME.items()}


def init(speaker_model: str | None) -> None:
    """ Initialized the module.

    Arguments:
        speaker_model:
            Speaker model as reported by WAM API.
    """
    # It should not be possible to change model
    if _init:
        raise PywamError('Can only be initialized once')
    # Get info
    if not speaker_model:
        speaker_model = ''
    _model_info = SPEAKER_MODELS.get(speaker_model, SPEAKER_MODELS['UNRECOGNIZED'])
    # Model
    global _model_name
    _model_name = _model_info['name']
    # Volume
    global _max_api_volume, _vol_to_api, _vol_to_user
    _max_api_volume = _model_info['max_api_volume']
    _vol_to_api = _max_api_volume / 100
    _vol_to_user = 100 / _max_api_volume
    # Sources
    global _source_to_api, _source_to_user, _sources
    _sources = _model_info['sources']


def model(model: str | None = None) -> str:
    """ Translate or return speaker name. """
    if model is None:
        return _model_name
    else:
        _model_info = SPEAKER_MODELS.get(model, SPEAKER_MODELS['UNRECOGNIZED'])
        return _model_info['name']


def sources() -> list[str]:
    """ Return speaker sources. """
    return _sources


def encode_volume(volume: int) -> int:
    """ Translate volume to API values. """
    vol = int(volume * _vol_to_api)
    return min(max(vol, 0), _max_api_volume)


def decode_volume(volume: int) -> int:
    """ Translate volume to user value. """
    vol = int(volume * _vol_to_user)
    return min(max(vol, 0), 100)


def encode_source(source: str) -> str:
    """ Translate source to API value. """
    try:
        return _source_to_api[source]
    except KeyError:
        raise ValueError('Could not find source')


def decode_source(source: str) -> str:
    """ Translate source to user value. """
    return _source_to_user.get(source, 'Unknown')
