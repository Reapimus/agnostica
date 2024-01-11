"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TypedDict
from typing_extensions import NotRequired

from .comment import ContentComment
from .channel import Mentions
from .identifier import identifier

class ForumTopicSummary(TypedDict):
    id: identifier
    serverId: identifier
    groupId: identifier
    channelId: identifier
    title: str
    createdAt: str
    createdBy: identifier
    updatedAt: NotRequired[str]
    bumpedAt: NotRequired[str]
    isPinned: NotRequired[bool]
    isLocked: NotRequired[bool]

class ForumTopic(ForumTopicSummary):
    content: str
    mentions: NotRequired[Mentions]

class ForumTopicComment(ContentComment):
    forumTopicId: identifier
    mentions: NotRequired[Mentions]