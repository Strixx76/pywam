# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Library for communicating with Samsung Wireless Audio speakers (WAM). """

MAJOR_VERSION = 0
MINOR_VERSION = 0
PATCH_VERSION = 1

__author__ = 'Daniel Jönsson'
__version__ = f'{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}'
__license__ = 'MIT License'


# PEP 8: Module level "dunders" should be placed before any import
# statements except from __future__ imports.
import logging  # noqa: E402
import sys  # noqa: E402

MIN_REQUIRED_PY_VERSION = (3, 8, 0)

if sys.version_info[:3] < MIN_REQUIRED_PY_VERSION:
    raise ImportError('pywam requires at least Python {}.{}.{}'
                      .format(*MIN_REQUIRED_PY_VERSION))

logging.getLogger(__name__).addHandler(logging.NullHandler())
