"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import Literal, TypedDict
from typing_extensions import NotRequired

class SocialLink(TypedDict):
    type: Literal['twitch', 'bnet', 'psn', 'xbox', 'steam', 'origin', 'youtube', 'twitter', 'facebook', 'switch', 'patreon', 'roblox', 'epic']
    userId: str
    handle: NotRequired[str]
    serviceId: NotRequired[str]
    createdAt: str