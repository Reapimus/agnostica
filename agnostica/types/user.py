"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union
from typing_extensions import NotRequired

class UserStatus(TypedDict):
    content: NotRequired[str]
    emoteId: int

class UserSummary(TypedDict):
    id: str
    type: NotRequired[Literal['user', 'bot']]
    name: str
    avatar: NotRequired[Optional[str]]

class User(UserSummary):
    botId: NotRequired[str]
    createdBy: NotRequired[str]
    profilePicture: NotRequired[str]
    profilePictureSm: NotRequired[str]
    profilePictureLg: NotRequired[str]
    profilePictureBlur: NotRequired[str]
    banner: NotRequired[str]
    profileBannerSm: NotRequired[str]
    profileBannerLg: NotRequired[str]
    profileBannerBlur: NotRequired[str]
    createdAt: str
    subdomain: NotRequired[Optional[str]]
    email: NotRequired[Optional[str]]
    serviceEmail: NotRequired[Optional[str]]
    joinDate: NotRequired[str]
    lastOnline: NotRequired[str]
    steamId: NotRequired[str]
    stonks: NotRequired[int]
    badges: NotRequired[List[str]]
    flairInfos: NotRequired[Dict[str, Any]]
    teams: NotRequired[Union[Literal[False], List[Dict[str, Any]]]]
    status: NotRequired[UserStatus]

class ServerMemberSummary(TypedDict):
    user: UserSummary
    roleIds: List[int]

class ServerMember(ServerMemberSummary):
    user: User
    nickname: NotRequired[str]
    joinedAt: str
    isOwner: NotRequired[bool]

class ServerMemberBan(TypedDict):
    user: UserSummary
    reason: Optional[str]
    createdBy: str
    createdAt: str