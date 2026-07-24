"""Pytest configuration for the pywam test-suite.

The library lives under ``<repo>/src/pywam`` so we must put that ``src``
directory on ``sys.path`` before the tests import anything.

To let the SAME test-suite run against a different checkout (e.g. a
``master`` worktree, to prove a fix actually changes behaviour), the src
directory can be overridden with the ``PYWAM_SRC`` environment variable.
When it is unset we fall back to the ``src`` directory that sits next to
this ``tests`` directory.
"""
from __future__ import annotations

import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_default_src = os.path.join(os.path.dirname(_here), "src")

PYWAM_SRC = os.environ.get("PYWAM_SRC", _default_src)
sys.path.insert(0, PYWAM_SRC)
