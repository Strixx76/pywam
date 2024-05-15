"""Exceptions used by pywam."""
from __future__ import annotations


class PywamError(Exception):
    """ General pywam exception. """


class FeatureNotSupportedError(PywamError):
    """ Feature not supported by current mode or app. """


class ApiCallError(PywamError):
    """ Api call was not successful. """


class ApiCallTimeoutError(PywamError):
    """ Api call response time out. """
