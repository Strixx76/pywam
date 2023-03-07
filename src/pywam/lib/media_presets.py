# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Classes and function for handling media presets. """
from __future__ import annotations


class MediaPreset:
    """ Class for storing media presets. """

    def __init__(self,
                 cpname: str,
                 kind: str,
                 title: str,
                 description: str,
                 thumbnail: str,
                 contentid: str,
                 mediaid: str,
                 **kwargs) -> None:
        self._cpname = cpname
        self._kind = kind
        self._title = title
        self._description = description
        self._thumbnail = thumbnail
        self._contentid = contentid
        self._mediaid = mediaid

    @property
    def app(self) -> str:
        """ Return app name. Only 'TuneIn' seems to be supported? """
        return self._cpname

    @property
    def kind(self) -> str:
        """ Return kind. Either 'speaker' or 'my'. """
        return self._kind

    @property
    def title(self) -> str:
        """ Return title of radio station. """
        return self._title

    @property
    def description(self) -> str:
        """ Return station description. """
        return self._description

    @property
    def thumbnail(self) -> str:
        """ Return URL to station logo thumbnail. """
        return self._thumbnail

    @property
    def contentid(self) -> str:
        """ Return number in preset list. Used for playing the preset. """
        return self._contentid

    @property
    def mediaid(self) -> str:
        """ Return ID on TuneIn. """
        return self._mediaid
