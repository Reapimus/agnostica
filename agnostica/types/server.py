"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import Optional, TypedDict
from typing_extensions import NotRequired

class Server(TypedDict):
    id: str
    name: str
    ownerId: str
    type: Optional[str]
    url: Optional[str]
    about: Optional[str]
    avatar: NotRequired[str]
    banner: NotRequired[str]
    timezone: NotRequired[str]
    isVerified: NotRequired[Optional[bool]]
    defaultChannelId: NotRequired[Optional[str]]
    createdAt: str