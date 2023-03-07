# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Collection of small helper functions for pywam. """


def listify(input_list):
    """ Ensure that the returned object is a list.

    Encapsulates all objects except None and lists in a list.
    """
    if input_list is None:
        return None
    if not input_list:
        return []
    if not isinstance(input_list, list):
        input_list = [input_list]
        return input_list
    else:
        return input_list


def timelength_to_sec(timelength: str) -> int:
    """ Convert API response data timelength to seconds. """

    if not isinstance(timelength, str):
        return 0

    # As for now only response format received is HH:MM:SS.uuu format
    tl = timelength.replace('.', ':')
    try:
        return int(sum(x * int(t) for x, t in
                       zip([0.001, 1, 60, 3600], reversed(tl.split(":"))))
                   )
    except Exception:
        return 0
