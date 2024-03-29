"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Tuple, Union

from .permissions import REVERSE_VALID_NAME_MAP, PermissionOverride

import datetime

if TYPE_CHECKING:
    from .types.category import (
        ChannelCategoryRolePermission as ChannelCategoryRolePermissionPayload,
        ChannelCategoryRolePermission as ChannelCategoryUserPermissionPayload,
    )
    from .types.channel import (
        ChannelRolePermission as ChannelRolePermissionPayload,
        ChannelUserPermission as ChannelUserPermissionPayload,
    )

    from .server import Server

__all__ = (
    'ChannelRoleOverride',
    'ChannelUserOverride',
    'CategoryRoleOverride',
    'CategoryUserOverride',
)

class _ChannelPermissionOverride:
    __slots__: Tuple[str, ...] = (
        'override',
        'created_at',
        'updated_at',
        'channel_id',
        'channel',
    )

    def __init__(
        self,
        *,
        data: Union[ChannelRolePermissionPayload, ChannelUserPermissionPayload],
        server: Optional[Server] = None,
    ):
        self.override = PermissionOverride(**{ REVERSE_VALID_NAME_MAP[key]: value for key, value in data['permissions'].items() })
        self.created_at: datetime.datetime = data['createdAt']
        self.updated_at: Optional[datetime.datetime] = data.get('updatedAt')
        self.channel_id = data['channelId']
        self.channel = server.get_channel(self.channel_id) if server else None


class ChannelRoleOverride(_ChannelPermissionOverride):
    """Represents a role-based permission override in a channel.

    Attributes
    -----------
    role: Optional[:class:`.Role`]
        The role whose permissions are to be overridden.
    role_id: :class:`int`
        The ID of the role.
    override: :class:`.PermissionOverride`
        The permission values overridden for the role.
    channel: Optional[:class:`.abc.ServerChannel`]
        The channel that the override is in.
    channel_id: :class:`str`
        The ID of the channel.
    created_at: :class:`datetime.datetime`
        When the override was created.
    updated_at: Optional[:class:`datetime.datetime`]
        When the override was last updated.
    """

    __slots__: Tuple[str, ...] = (
        'role_id',
        'role',
    )

    def __init__(self, *, data: ChannelRolePermissionPayload, server: Optional[Server] = None):
        super().__init__(data=data, server=server)
        self.role_id = data['roleId']
        self.role = server.get_role(self.role_id) if server else None

    def __repr__(self) -> str:
        return f'<ChannelRoleOverride override={self.override!r} channel_id={self.channel_id!r} role_id={self.role_id!r}>'


class ChannelUserOverride(_ChannelPermissionOverride):
    """Represents a user-based permission override in a channel.

    Attributes
    -----------
    user: Optional[:class:`.Member`]
        The user whose permissions are to be overridden.
    user_id: :class:`str`
        The ID of the user.
    override: :class:`.PermissionOverride`
        The permission values overridden for the user.
    channel: Optional[:class:`.abc.ServerChannel`]
        The channel that the override is in.
    channel_id: :class:`str`
        The ID of the channel.
    created_at: :class:`datetime.datetime`
        When the override was created.
    updated_at: Optional[:class:`datetime.datetime`]
        When the override was last updated.
    """

    __slots__: Tuple[str, ...] = (
        'user_id',
        'user',
    )

    def __init__(self, *, data: ChannelUserPermissionPayload, server: Optional[Server] = None):
        super().__init__(data=data, server=server)
        self.user_id = data['userId']
        self.user = server.get_member(self.user_id) if server else None

    def __repr__(self) -> str:
        return f'<ChannelUserOverride override={self.override!r} channel_id={self.channel_id!r} user_id={self.user_id!r}>'

class _CategoryPermissionOverride:
    __slots__: Tuple[str, ...] = (
        'override',
        'created_at',
        'updated_at',
        'category_id',
        'category',
    )

    def __init__(
        self,
        *,
        data: Union[ChannelCategoryRolePermissionPayload, ChannelCategoryUserPermissionPayload],
        server: Optional[Server] = None,
    ):
        self.override = PermissionOverride(**{ REVERSE_VALID_NAME_MAP[key]: value for key, value in data['permissions'].items() })
        self.created_at: datetime.datetime = data['createdAt']
        self.updated_at: Optional[datetime.datetime] = data.get('updatedAt')
        self.category_id = data['categoryId']
        self.category = server.get_category(self.category_id) if server else None

class CategoryRoleOverride(_CategoryPermissionOverride):
    """Represents a role-based permission override in a category.

    Attributes
    -----------
    role: Optional[:class:`.Role`]
        The role whose permissions are to be overridden.
    role_id: :class:`int`
        The ID of the role.
    override: :class:`.PermissionOverride`
        The permission values overridden for the role.
    category: Optional[:class:`.Category`]
        The category that the override is in.
    category_id: :class:`int`
        The ID of the category.
    created_at: :class:`datetime.datetime`
        When the override was created.
    updated_at: Optional[:class:`datetime.datetime`]
        When the override was last updated.
    """

    __slots__: Tuple[str, ...] = (
        'role_id',
        'role',
    )

    def __init__(self, *, data: ChannelRolePermissionPayload, server: Optional[Server] = None):
        super().__init__(data=data, server=server)
        self.role_id = data['roleId']
        self.role = server.get_role(self.role_id) if server else None

    def __repr__(self) -> str:
        return f'<CategoryRoleOverride override={self.override!r} category_id={self.category_id!r} role_id={self.role_id!r}>'

class CategoryUserOverride(_CategoryPermissionOverride):
    """Represents a user-based permission override in a category.

    Attributes
    -----------
    user: Optional[:class:`.Member`]
        The user whose permissions are to be overridden.
    user_id: :class:`str`
        The ID of the user.
    override: :class:`.PermissionOverride`
        The permission values overridden for the user.
    category: Optional[:class:`.Category`]
        The category that the override is in.
    category_id: :class:`int`
        The ID of the category.
    created_at: :class:`datetime.datetime`
        When the override was created.
    updated_at: Optional[:class:`datetime.datetime`]
        When the override was last updated.
    """

    __slots__: Tuple[str, ...] = (
        'user_id',
        'user',
    )

    def __init__(self, *, data: ChannelUserPermissionPayload, server: Optional[Server] = None):
        super().__init__(data=data, server=server)
        self.user_id = data['userId']
        self.user = server.get_member(self.user_id) if server else None

    def __repr__(self) -> str:
        return f'<CategoryRoleOverride override={self.override!r} category_id={self.category_id!r} user_id={self.user_id!r}>'