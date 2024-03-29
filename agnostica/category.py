"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from .mixins import Hashable
from .override import CategoryRoleOverride, CategoryUserOverride
from .globals import platform

import datetime

if TYPE_CHECKING:
    from .types.category import Category as CategoryPayload

    from .group import Group
    from .permissions import PermissionOverride
    from .role import Role
    from .server import Server
    from .user import Member

__all__ = (
    'Category',
    'CategoryChannel',
)


class Category(Hashable):
    """Represents a channel category.

    .. container:: operations

        .. describe:: x == y

            Checks if two categories are equal.

        .. describe:: x != y

            Checks if two categories are not equal.

        .. describe:: hash(x)

            Returns the category's hash.

        .. describe:: str(x)

            Returns the name of the category.

    Attributes
    -----------
    id: :class:`int`
        The category's ID.
    name: :class:`str`
        The category's name.
    priority: Optional[:class:`int`]
        The priority of the category in relation to other categories in the
        group. Higher values are displayed higher in the UI. If this is ``None``,
        the category is to be sorted descending by :attr:`.created_at`.
    created_at: :class:`datetime.datetime`
        When the category was created.
    updated_at: Optional[:class:`datetime.datetime`]
        When the category was last updated.
    server_id: :class:`str`
        The ID of the server that the category is in.
    group_id: :class:`str`
        The ID of the group that the category is in.
    """

    __slots__: Tuple[str, ...] = (
        '_state',
        '_server',
        '_group',
        '_platform',
        'id',
        'name',
        'server_id',
        'group_id',
        'created_at',
        'updated_at',
        'priority',
    )

    def __init__(self, *, state, _platform, data: CategoryPayload, **extra):
        self._state = state
        self._platform = _platform or platform
        self._server: Optional[Server] = extra.get('server')
        self._group: Optional[Group] = extra.get('group')

        self.id: int = data['id']
        self.name: str = data.get('name') or ''
        self.server_id: str = data.get('serverId')
        self.group_id: str = data.get('groupId')
        self.created_at: datetime.datetime = data.get('createdAt')
        self.updated_at: Optional[datetime.datetime] = data.get('updatedAt')
        self.priority: Optional[int] = data.get('priority')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Category id={self.id!r} name={self.name!r} group={self.group!r}>'

    @property
    def group(self) -> Optional[Group]:
        """Optional[:class:`~agnostica.Group`]: The group that this category is in."""
        group = self._group
        if not group and self.server:
            group = self.server.get_group(self.group_id)

        return group

    @property
    def server(self) -> Server:
        """:class:`.Server`: The server that this category is in."""
        return self._group.server if self._group else self._server or self._state._get_server(self.server_id)

    @property
    def guild(self) -> Server:
        """:class:`.Server`:

        This is an alias of :attr:`.server`.

        The server that this category is in.
        """
        return self.server

    def is_nsfw(self) -> bool:
        """:class:`bool`:

        Always returns ``False``.
        """
        return False

    async def edit(self, *, name: str = None, priority: int = None) -> Category:
        """|coro|

        Edit this category.

        All parameters are optional.

        Parameters
        -----------
        name: :class:`str`
            The category's name.
        priority: :class:`int`
            The category's priority.

            .. versionadded:: 1.12

        Returns
        --------
        :class:`.Category`
            The newly edited category.
        """

        payload = {}
        if name is not None:
            payload['name'] = name
        if priority is not None:
            payload['priority'] = priority

        data = await self._platform.update_category(self.server_id, self.id, payload=payload)
        return Category(state=self._state, _platform=self._platform, data=data, group=self._group, server=self._server)

    async def create_role_override(self, role: Role, override: PermissionOverride) -> CategoryRoleOverride:
        """|coro|

        Create a role-based permission override in this category.

        Parameters
        -----------
        role: :class:`.Role`
            The role to create an override for.
        override: :class:`.PermissionOverride`
            The override values to use.

        Returns
        --------
        :class:`.CategoryRoleOverride`
            The created role override.
        """

        data = await self._platform.create_category_role_override(
            self.server_id,
            self.id,
            role.id,
            permissions=override.to_dict(),
        )
        return CategoryRoleOverride(data=data, server=self.server)

    async def fetch_role_override(self, role: Role) -> CategoryRoleOverride:
        """|coro|

        Fetch a role-based permission override in this category.

        Parameters
        -----------
        role: :class:`.Role`
            The role whose override to fetch.

        Returns
        --------
        :class:`.CategoryRoleOverride`
            The role override.
        """

        data = await self._platform.get_category_role_override(
            self.server_id,
            self.id,
            role.id,
        )
        return CategoryRoleOverride(data=data, server=self.server)

    async def fetch_role_overrides(self) -> List[CategoryRoleOverride]:
        """|coro|

        Fetch all role-based permission overrides in this category.

        Returns
        --------
        List[:class:`.CategoryRoleOverride`]
            The role overrides.
        """

        data = await self._platform.get_category_role_overrides(self.server_id, self.id)
        return [
            CategoryRoleOverride(data=override_data, server=self.server)
            for override_data in data
        ]

    async def update_role_override(self, role: Role, override: PermissionOverride) -> CategoryRoleOverride:
        """|coro|

        Update a role-based permission override in this category.

        Parameters
        -----------
        role: :class:`.Role`
            The role to update an override for.
        override: :class:`.PermissionOverride`
            The new override values to use.

        Returns
        --------
        :class:`.CategoryRoleOverride`
            The updated role override.
        """

        data = await self._platform.update_category_role_override(
            self.server_id,
            self.id,
            role.id,
            permissions=override.to_dict(),
        )
        return CategoryRoleOverride(data=data, server=self.server)

    async def delete_role_override(self, role: Role) -> None:
        """|coro|

        Delete a role-based permission override in this category.

        Parameters
        -----------
        role: :class:`.Role`
            The role whose override to delete.
        """

        await self._platform.delete_category_role_override(
            self.server_id,
            self.id,
            role.id,
        )

    async def create_user_override(self, user: Member, override: PermissionOverride) -> CategoryUserOverride:
        """|coro|

        Create a user-based permission override in this category.

        Parameters
        -----------
        user: :class:`.Member`
            The user to create an override for.
        override: :class:`.PermissionOverride`
            The override values to use.

        Returns
        --------
        :class:`.CategoryUserOverride`
            The created user override.
        """

        data = await self._platform.create_category_user_override(
            self.server_id,
            self.id,
            user.id,
            permissions=override.to_dict(),
        )
        return CategoryUserOverride(data=data, server=self.server)

    async def fetch_user_override(self, user: Member) -> CategoryUserOverride:
        """|coro|

        Fetch a user-based permission override in this category.

        Parameters
        -----------
        user: :class:`.Member`
            The user whose override to fetch.

        Returns
        --------
        :class:`.CategoryUserOverride`
            The role override.
        """

        data = await self._platform.get_category_user_override(
            self.server_id,
            self.id,
            user.id,
        )
        return CategoryUserOverride(data=data, server=self.server)

    async def fetch_user_overrides(self) -> List[CategoryUserOverride]:
        """|coro|

        Fetch all user-based permission overrides in this category.

        Returns
        --------
        List[:class:`.CategoryUserOverride`]
            The role overrides.
        """

        data = await self._platform.get_category_user_overrides(self.server_id, self.id)
        return [
            CategoryUserOverride(data=override_data, server=self.server)
            for override_data in data
        ]

    async def update_user_override(self, user: Member, override: PermissionOverride) -> CategoryUserOverride:
        """|coro|

        Update a user-based permission override in this category.

        Parameters
        -----------
        user: :class:`.Member`
            The user to update an override for.
        override: :class:`.PermissionOverride`
            The new override values to use.

        Returns
        --------
        :class:`.CategoryUserOverride`
            The updated role override.
        """

        data = await self._platform.update_category_user_override(
            self.server_id,
            self.id,
            user.id,
            permissions=override.to_dict(),
        )
        return CategoryUserOverride(data=data, server=self.server)

    async def delete_user_override(self, user: Member) -> None:
        """|coro|

        Delete a user-based permission override in this category.

        Parameters
        -----------
        user: :class:`.Member`
            The user whose override to delete.
        """

        await self._platform.delete_category_user_override(
            self.server_id,
            self.id,
            user.id,
        )

    async def delete(self) -> Category:
        """|coro|

        Delete this category.

        This method will not delete the category's channels.

        Returns
        --------
        :class:`.Category`:
            The deleted category.
        """

        data = await self._platform.delete_category(self.server_id, self.id)
        return Category(state=self._state, _platform=self._platform, data=data, group=self._group, server=self._server)

CategoryChannel = Category  # discord.py