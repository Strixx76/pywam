# This file is part of the pywam project.
# Copyright (c) Daniel Jönsson. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in project root.

""" Api response handling. """

from collections import defaultdict
from typing import Any
import xml.etree.ElementTree as ET


class ApiResponse:
    """ Messages from the speaker and socket connection.

    Contains speaker events (API responses) and error messages from both
    speaker and methods that are involved in getting responses from the
    speaker.

    Attributes:
        raw_response:
            Raw XML-string from speaker.
        api_type:
            Type of API call. (XML-node: type)
        method:
            Name of response (XML-node: method)
        user:
            Sender of API call. (XML-node: user_identifier)
        version:
            API-version. (XML-node: version)
        speaker_ip:
            Speaker IP address. (XML-node: speakerip)
        success:
            True if call was successful.
            (XML-node "response" attribute "result")
        data:
            Requested data (XML-node: response).
        err_msg:
            Description of what and/or where something went wrong.
        err_repr:
            String representation of the exception that caused the
            error response.
    """
    __slots__ = ('raw_response', 'api_type', 'method', 'user',
                 'version', 'speaker_ip', 'success', 'data',
                 'err_msg', 'err_repr')

    def __init__(self,
                 raw_response: str = '',
                 api_type: str = '',
                 method: str = '',
                 user: str = '',
                 version: str = '',
                 speaker_ip: str = '',
                 success: bool = False,
                 data: Any = None,
                 err_msg: str = '',
                 err_repr: str = '',
                 ) -> None:
        self.raw_response = raw_response
        self.api_type = api_type
        self.method = method
        self.user = user
        self.version = version
        self.speaker_ip = speaker_ip
        self.success = success
        self.data = data
        self.err_msg = err_msg
        self.err_repr = err_repr

    def __str__(self) -> str:
        return ('ApiResponse:\n' +
                f' raw_response: {self.raw_response}\n' +
                f' api_type: {self.api_type}\n' +
                f' method: {self.method}\n' +
                f' user: {self.user}\n' +
                f' version: {self.version}\n' +
                f' speaker_ip: {self.speaker_ip}\n' +
                f' success: {self.success}\n' +
                f' data: {self.data}\n' +
                f' err_msg: {self.err_msg}\n' +
                f' err_repr: {self.err_repr}\n'
                )

    def get_key(self, key: str, default: Any = None) -> Any:
        """ Get a value from data.

        Arguments:
            key:
                Key for value to return.
            default:
                Value to return if key can not be found.

        Returns:
            Value for the given key if the key exists,
            otherwise given default value.
        """
        if isinstance(self.data, dict):
            return self.data.get(key, default)
        return default

    def get_subkey(self, key, subkey, default: Any = None) -> Any:
        """ Get a value from data.

        Arguments:
            key:
                Key in which the sub key should be.
            subkey:
                Key for value to return.
            default:
                Value to return if key can not be found.

        Returns:
            Value for the given key if the key exists,
            otherwise given default value.
        """
        if isinstance(self.data, dict):
            if value := self.data.get(key):
                return value.get(subkey, default)
        return default


def api_decode(raw_response: str) -> ApiResponse:
    """ Parse XML to ApiResponse.

    Arguments:
        raw_response:
            XML response from speaker.

    Returns:
        :class:`ApiResponse` with parsed response from speaker.
    """
    def xml_to_dict(node: ET.Element) -> dict:
        """ Convert an ElementTree.Element to a Python dictionary.

        Arguments:
            node:
                ElementTree.Element to be converted.

        Returns:
            Python dictionary with the converted XML tree.
        """
        resp: dict[str, Any] = {node.tag: {} if node.attrib else None}

        children = list(node)
        if len(node) > 0:
            dd: dict[str, Any] = defaultdict(list)
            for dc in map(xml_to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            resp = {node.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if node.attrib:
            resp[node.tag].update(('@' + k, v) for k, v in node.attrib.items())
        if node.text:
            text = node.text.strip() or ''
            if children or node.attrib:
                if text:
                    resp[node.tag]['#text'] = text
            else:
                resp[node.tag] = text
        return resp

    root = ET.fromstring(raw_response)
    root_dict = xml_to_dict(root)
    response_dict = root_dict[root.tag]
    response_dict['type'] = root.tag

    # One response ('GlobalSearch') found where data is in 'async_response'
    # instead of 'response'. Needs more investigation.
    data = response_dict.get('response', {})
    success = (data.get('@result') == 'ok')

    return ApiResponse(raw_response=raw_response,
                       api_type=response_dict.get('type', ''),
                       method=response_dict.get('method', ''),
                       user=response_dict.get('user_identifier', ''),
                       version=response_dict.get('version', ''),
                       speaker_ip=response_dict.get('speakerip', ''),
                       success=success,
                       data=data,
                       )


def api_error(msg: str,
              error: Exception | None = None,
              raw_response: str = '',
              ) -> ApiResponse:
    """ Create ApiResponse from a Exception.

    Arguments:
        msg:
            Description of what and/or where something went wrong.
        error (optional):
            Exception that caused this message to be created.
        raw_response (optional):
            XML response from speaker..

    Returns:
        :class:`ApiResponse` with information about the error that
        occurred.

    """
    return ApiResponse(err_msg=msg,
                       err_repr=repr(error),
                       raw_response=raw_response,
                       )
