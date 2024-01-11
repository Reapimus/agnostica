"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse

    from .types.http import HTTPError as HTTPErrorPayload

class AgnosticaException(Exception):
    """Base class for all agnostica exceptions."""
    pass

class ClientException(AgnosticaException):
    """Thrown when an operation in the client class fails."""
    pass

class HTTPException(AgnosticaException):
    """A non-ok response from the platform was returned whilst performing an
    HTTP request."""
    def __init__(self, response: ClientResponse, data: HTTPErrorPayload):
        self.response = response
        self.status = response.status
        self.message: str = ''
        self.code: str = ''
        self._meta: dict = {}
        if isinstance(data, dict):
            self.message: str = data.get('message') or ''
            self.code: str = data.get('code', 'Unknown')
            self._meta = data.get('meta', {})
        super().__init__(f'{self.status} ({self.code}): {self.message}')

class BadRequest(HTTPException):
    """Thrown on a status code 400"""
    pass

class PlatformServerError(HTTPException):
    """Thrown on a status code 500"""
    pass

class TooManyRequests(HTTPException):
    """Thrown on a status code 429"""
    pass

class ImATeapot(HTTPException):
    """Thrown on a status code 418"""
    pass

class NotFound(HTTPException):
    """Thrown on a status code 404"""
    pass

class Forbidden(HTTPException):
    """Thrown on a status code 403"""
    pass

    @property
    def raw_missing_permissions(self):
        return self._meta.get('missingPermissions', [])

class InvalidData(ClientException):
    """An exception that is raised when an adapter encounters
    unknown or invalid data from their platform."""
    pass

class InvalidArgument(ClientException):
    """An exception that is raised when an argument to a
    function is invalid in some way."""
    pass