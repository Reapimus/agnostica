"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TypedDict
from typing_extensions import NotRequired

from .channel import Mentions
from .comment import ContentComment
from .identifier import identifier

class Announcement(TypedDict):
    id: identifier
    serverId: identifier
    groupId: identifier
    channelId: identifier
    title: str
    content: str
    mentions: NotRequired[Mentions]
    createdAt: str
    createdBy: identifier

class AnnouncementComment(ContentComment):
    announcementId: identifier
    mentions: NotRequired[Mentions]