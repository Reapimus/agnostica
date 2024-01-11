"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations

from typing import Optional, TypedDict
from typing_extensions import NotRequired

class PartialWebhook(TypedDict):
    id: str
    name: str
    token: NotRequired[Optional[str]]
    channelId: NotRequired[str]
    deletedAt: NotRequired[str]
    createdAt: NotRequired[str]

class _UserWebhook(TypedDict, total=False):
    teamId: str
    iconUrl: Optional[str]
    createdBy: NotRequired[str]

class _Webhook(TypedDict, total=False):
    avatar: NotRequired[str]
    serverId: str

class Webhook(PartialWebhook, _UserWebhook, _Webhook):
    ...