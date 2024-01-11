"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TypedDict, List
from typing_extensions import NotRequired

class HTTPError(TypedDict):
    code: str
    message: str
    meta: NotRequired[HTTPErrorMeta]

class HTTPErrorMeta(TypedDict):
    missingPermissions: NotRequired[List[str]]