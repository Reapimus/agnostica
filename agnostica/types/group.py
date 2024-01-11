"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TypedDict
from typing_extensions import NotRequired

class Group(TypedDict):
    id: str
    serverId: str
    name: str
    description: NotRequired[str]
    avatar: NotRequired[str]
    isHome: NotRequired[bool]
    emoteId: NotRequired[int]
    isPublic: NotRequired[bool]
    createdAt: str
    createdBy: str
    updatedAt: NotRequired[str]
    updatedBy: NotRequired[str]
    archivedAt: NotRequired[str]
    archivedBy: NotRequired[str]