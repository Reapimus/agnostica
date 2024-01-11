"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TypedDict
from typing_extensions import NotRequired

from .channel import Mentions

class ListItemNoteSummary(TypedDict):
    createdAt: str
    createdBy: str
    updatedAt: NotRequired[str]
    updatedBy: NotRequired[str]

class ListItemSummary(TypedDict):
    id: str
    serverId: str
    channelId: str
    message: str
    mentions: NotRequired[Mentions]
    createdAt: str
    createdBy: str
    createdByWebhookId: NotRequired[str]
    updatedAt: NotRequired[str]
    updatedBy: NotRequired[str]
    parentListItemId: NotRequired[str]
    completedAt: NotRequired[str]
    completedBy: NotRequired[str]
    note: NotRequired[ListItemNoteSummary]

class ListItemNote(ListItemNoteSummary):
    mentions: NotRequired[Mentions]
    content: str

class ListItem(ListItemSummary):
    groupId: str
    note: NotRequired[ListItemNote]