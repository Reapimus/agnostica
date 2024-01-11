"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import List, TypedDict
from typing_extensions import NotRequired

class Role(TypedDict):
    id: int
    serverId: str
    createdAt: str
    updatedAt: NotRequired[str]
    name: str
    isDisplayedSeparately: NotRequired[bool]
    isSelfAssignable: NotRequired[bool]
    isMentionable: NotRequired[bool]
    permissions: List[str]
    colors: NotRequired[List[int]]
    icon: NotRequired[str]
    priority: int
    isBase: NotRequired[bool]
    botUserId: NotRequired[str]