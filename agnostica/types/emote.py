"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TypedDict
from typing_extensions import NotRequired

class Emote(TypedDict):
    id: int
    name: str
    url: str
    serverId: NotRequired[str]