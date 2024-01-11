"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import Dict, List, Literal, Optional, TypedDict
from typing_extensions import NotRequired

from .user import User
from .role import Role
from .identifier import identifier

class ServerChannel(TypedDict):
    id: identifier
    type: str
    name: str
    topic: Optional[str]
    createdAt: str
    createdBy: identifier
    updatedAt: NotRequired[str]
    serverId: identifier
    rootId: NotRequired[identifier]
    parentId: NotRequired[identifier]
    messageId: NotRequired[identifier]
    categoryId: NotRequired[identifier]
    groupId: identifier
    visibility: NotRequired[Optional[Literal['private', 'public']]]
    isPublic: NotRequired[bool]
    archivedBy: NotRequired[identifier]
    archivedAt: NotRequired[str]

class Thread(ServerChannel):
    rootId: identifier
    parentId: identifier

class Mentions(TypedDict):
    users: Optional[List[User]]
    channels: Optional[List[ServerChannel]]
    roles: Optional[List[Role]]
    everyone: bool
    here: bool

class ChannelRolePermission(TypedDict):
    permissions: Dict[str, bool]
    createdAt: str
    updatedAt: NotRequired[str]
    roleId: identifier
    channelId: identifier

class ChannelUserPermission(TypedDict):
    permissions: Dict[str, bool]
    createdAt: str
    updatedAt: NotRequired[str]
    userId: identifier
    channelId: identifier