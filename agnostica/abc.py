"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Sequence

from agnostica.http import HTTPClientBase

from .utils import MISSING
from .mixins import HasContentMixin, Hashable
from .globals import platform
from .enums import ChannelVisibility, UserType, try_enum
from .asset import Asset
from .file import File
from .presence import BasePresence
from .enums import ChannelType
from .message import ChatMessage
from .override import ChannelRoleOverride, ChannelUserOverride

import datetime
import abc

if TYPE_CHECKING:
    from typing_extensions import Self

    from .types.user import User as UserPayload
    from .types.channel import ServerChannel as ServerChannelPayload
    from .types.comment import ContentComment

    from .category import Category
    from .channel import Thread
    from .embed import Embed
    from .group import Group
    from .permissions import PermissionOverride
    from .role import Role
    from .server import Server
    from .user import Member

__all__ = (
    'GuildChannel',
    'Messageable',
    'Reply',
    'ServerChannel',
    'User',
)

class Messageable(metaclass=abc.ABCMeta):
    """An ABC for models that messages can be sent to."""
    def __init__(self, *, state, _platform, data):
        self._state = state
        self._platform = _platform or platform
        self.id = data.get('id')
        self._channel_id = data.get('id')
    
    @property
    def _channel(self) -> Messageable:
        if isinstance(self, User):
            return self.dm_channel
        elif hasattr(self, 'channel'):
            return self.channel
        else:
            return self
    
    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
        embed: Optional[Embed] = MISSING,
        embeds: List[Embed] = MISSING,
        file: Optional[File] = MISSING,
        files: List[File] = MISSING,
        delete_after: Optional[float] = None,
        reference: Optional[ChatMessage] = None,
        mention_author: Optional[bool] = None,
        silent: Optional[bool] = None,
        private: Optional[bool] = None,
        hide_preview_urls: Optional[Sequence[str]] = MISSING,
    ) -> ChatMessage:
        """|coro|
        
        Sends a message to the destination with the given content.
        
        Parameters
        -----------
        content: Optional[:class:`str`]
            The content of the message to send.
        embed: Optional[:class:`.Embed`]
            The embed to send with the message.
        embeds: List[:class:`.Embed`]
            A list of embeds to send with the message.
        file: Optional[:class:`.File`]
            The file to send with the message.
        files: List[:class:`.File`]
            A list of files to send with the message.
        delete_after: Optional[:class:`float`]
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.
        reference: Optional[:class:`.ChatMessage`]
            If provided, the message that this message references.
        mention_author: Optional[:class:`bool`]
            If provided, whether or not to mention the author of the message.
        """
        raise NotImplementedError
    
    async def history(self,
        *,
        before: Optional[datetime.datetime] = None,
        after: Optional[datetime.datetime] = None,
        limit: int = 50,
        include_private: bool = False
    ) -> List[ChatMessage]:
        """|coro|
        
        Gets the message history for the destination.
        
        Parameters
        -----------
        before: :class:`datetime.datetime`
            The timestamp to retrieve messages before.
        after: :class:`datetime.datetime`
            The timestamp to retrieve messages after.
        limit: :class:`int`
            The maximum number of messages to fetch. Defaults to 50.
        include_private: :class:`bool`
            Whether to include private messages in the response. Defaults to ``False``.
            If the client is a user account, this has no effect and is always ``True``.
        
        Returns
        --------
        List[:class:`.ChatMessage`]
        """
        raise NotImplementedError
    
    async def fetch_message(self, message_id: str, /) -> ChatMessage:
        """|coro|
        
        Fetch a message.
        
        Returns
        --------
        :class:`.ChatMessage`
        """
        raise NotImplementedError
    
    async def create_thread(
        self,
        name: str,
        *,
        message: Optional[ChatMessage] = None,
        visibility: ChannelVisibility
    ) -> Thread:
        """|coro|
        
        Create a new thread in the channel.
        
        Parameters
        -----------
        name: :class:`str`
            The thread's name. Adapters will automatically convert
            this to fit platform requirements.
        message: Optional[:class:`.ChatMessage`]
            The message to create the thread with.
            If a private message is passed (i.e. :attr:`.ChatMessage.private`
            is ``True``), then the thread is private too.
        visibility: Optional[:class:`.ChannelVisibility`]
            What users can access the channel.
        
        Returns
        --------
        :class:`.Thread`
        """
        raise NotImplementedError
    
    async def pins(self) -> List[ChatMessage]:
        """|coro|
        
        Fetch the list of pinned messages in this channel.
        
        Returns
        --------
        List[:class:`.ChatMessage`]
        """
        raise NotImplementedError

class User(Hashable, metaclass=abc.ABCMeta):
    """An ABC for user-type models.
    
    Attributes
    -----------
    id: :class:`str`
        The user's id.
    name: :class:`str`
        The user's name.
    bot_id: Optional[:class:`str`]
        The user's corresponding bot ID, if any.
        This will likely only be available for the connected :class:`.ClientUser`.
    avatar: Optional[:class:`.Asset`]
        The user's set avatar, if any.
    banner: Optional[:class:`.Asset`]
        The user's profile banner, if any.
    created_at: Optional[:class:`datetime.datetime`]
        When the user's account was created.
        This may be ``None`` if the user object was partial.
    status: Optional[:class:`.Status`]
        The custom status set by the user.
    """
    default_avatar: Optional[Asset] = None # This gets implemented by the adapter's user class

    __slots__ = (
        'type',
        '_user_type',
        'id',
        'bot_id',
        'dm_channel',
        'name',
        'nick',
        'bio',
        'tagline',
        'presence',
        'status',
        'blocked_at',
        'online_at',
        'created_at',
        'avatar',
        'banner',
        'badges',
    )

    def __init__(self, *, state: HTTPClientBase, data: UserPayload, **extra):
        self._state = state
        self._platform = platform

        self.type = None
        self._user_type = try_enum(UserType, data.get('type', 'user'))
        self.id: str = data.get('id')
        self.bot_id: Optional[str] = data.get('botId')
        self.dm_channel: Optional[ServerChannel] = data.get('dmChannel')
        self.name: str = data.get('name', '')
        self.nick: Optional[str] = None
        self.bio: str = data.get('aboutInfo', data.get('bio', ''))
        self.tagline: Optional[str] = data.get('tagline')
        self.slug: Optional[str] = data.get('slug')
        self.presence: BasePresence = data.get('userPresence')
        self.status = data.get('status')

        self.blocked_at: Optional[datetime.datetime] = data.get('blockedAt')
        self.online_at: Optional[datetime.datetime] = data.get('onlineAt')
        self.created_at: datetime.datetime = data.get('createdAt')

        self.avatar: Optional[Asset] = data.get('avatar')
        self.banner: Optional[Asset] = data.get('banner')

        self.badges: List = data.get('badges', []) # TODO: Create a Badge class that this will use for better cross-platform support

    def __str__(self) -> str:
        return self.display_name or ''
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} name={self.name!r} type={self._user_type!r}>'
    
    @property
    def profile_url(self) -> str:
        if self._platform.get_user_profile_url is not None:
            return self._platform.get_user_profile_url(self)
        if self._platform.PROFILE_BASE:
            return f'{self._platform.PROFILE_BASE}/{self.id}'
        return self._platform.BASE # Fallback URL for compatibility
    
    @property
    def vanity_url(self) -> str:
        if self.slug:
            if self._platform.get_user_vanity_url is not None:
                return self._platform.get_user_vanity_url(self)
            if self._platform.VANITY_BASE:
                return f'{self._platform.VANITY_BASE}/{self.slug}'
            elif platform.PROFILE_BASE:
                # Try to fallback to the Profile URL if Vanity URL is not available
                return f'{self._platform.PROFILE_BASE}/{self.id}'
        return None
    
    @property
    def mention(self) -> str:
        """:class:`str`: The mention string for this user.

        This will render and deliver a mention when sent in a :class:`.Message`.
        """
        return f'<@{self.id}>'
    
    @property
    def display_name(self) -> str:
        return self.nick if self.nick is not None else self.name
    
    @property
    def _channel_id(self) -> Optional[str]:
        return self.dm_channel.id if self.dm_channel else None
    
    @property
    def bot(self) -> bool:
        """:class:`bool`:

        Whether the user is a bot account or webhook.
        """
        return self._user_type is UserType.bot
    
    @property
    def display_avatar(self) -> Asset:
        """:class:`.Asset`: The "top-most" avatar for this user, or, the avatar
        that the client will display in the member list and in chat."""
        return self.avatar or self.default_avatar

class ServerChannel(Hashable, metaclass=abc.ABCMeta):
    """An ABC for various types of server channels."""

    def __init__(self, *, state: HTTPClientBase, data: ServerChannelPayload, group: Optional[Group] = None, **extra):
        self._state = state
        self._group = group
        self._platform = platform

        self.group_id: Optional[str] = data.get('groupId')
        self.server_id: Optional[str] = data.get('serverId')
        self.category_id: Optional[str] = data.get('categoryId')

        self.id: str = data.get('id')
        self.type: ChannelType = try_enum(ChannelType, data.get('type'))
        self.name: str = data.get('name') or ''
        self.topic: str = data.get('topic') or ''
        self.visibility: Optional[ChannelVisibility] = try_enum(ChannelVisibility, data.get('visibility', None))
        self.nsfw: Optional[bool] = data.get('nsfw', None)

        self.created_by_id: Optional[str] = extra.get('createdBy')
        self.created_at: datetime.datetime = data.get('createdAt')
        self.updated_at: datetime.datetime = data.get('updatedAt')

        self.archived_by_id: Optional[str] = data.get('archivedBy')
        self.archived_at: Optional[datetime.datetime] = data.get('archivedAt')
    
    @property
    def share_url(self) -> str:
        """:class:`str`: The share URL of the channel."""
        return self._platform.share_url(self)
    
    jump_url = share_url

    @property
    def mention(self) -> str:
        if self._platform.channel_mention:
            # Just in case a platform uses a special mention format
            return self._platform.channel_mention(self)
        return f'<#{self.id}>'
    
    @property
    def group(self) -> Optional[Group]:
        """Optional[:class:`~agnostica.Group`]: The group that this channel is in."""
        group = self._group
        if not group and self.server:
            group = self.server.get_group(self.group_id)

        return group

    @property
    def server(self) -> Server:
        """:class:`.Server`: The server that this channel is in."""
        return self._state._get_server(self.server_id)

    @property
    def guild(self) -> Server:
        """:class:`.Server`:

        This is an alias of :attr:`.server`.

        The server that this channel is in.
        """
        return self.server
    
    @property
    def category(self) -> Optional[Category]:
        """Optional[:class:`.Category`]: The category that this channel is in, if any."""
        if self.category_id and self.server:
            return self.server.get_category(self.category_id)

        return None

    @property
    def parent(self) -> Optional[ServerChannel]:
        return self.server.get_channel_or_thread(self.parent_id)

    @property
    def created_by(self) -> Optional[Member]:
        return self.server.get_member(self.created_by_id)

    @property
    def archived_by(self) -> Optional[Member]:
        return self.server.get_member(self.archived_by_id)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} name={self.name!r} server={self.server!r}>'

    def is_nsfw(self) -> bool:
        """:class:`bool`:"""
        if self._platform.is_channel_nsfw is not None:
            return self._platform.is_channel_nsfw(self)
        elif self.nsfw is not None:
            return self.nsfw
        
        return False
    
    async def edit(
        self,
        *,
        name: str = MISSING,
        topic: str = MISSING,
        visibility: ChannelVisibility = MISSING,
    ) -> Self:
        """|coro|

        Edit this channel.

        All parameters are optional.

        Parameters
        -----------
        name: :class:`str`
            The channel's name.
        topic: :class:`str`
            The channel's topic. Not applicable to threads.
        visibility: :class:`.ChannelVisibility`
            What users can access the channel.
            Could be ``None`` to reset the visibility.

        Returns
        --------
        :class:`.ServerChannel`
            The newly edited channel.
        """

        payload = {}
        if name is not MISSING:
            payload['name'] = name

        if topic is not MISSING:
            payload['topic'] = topic

        if visibility is not MISSING:
            payload['visibility'] = visibility.value if visibility is not None else None

        data = await self._platform.update_channel(
            self,
            payload=payload,
        )
        channel: Self = self._state.create_channel(
            data=data,
            group=self.group,
        )
        return channel
    
    async def create_role_override(self, role: Role, override: PermissionOverride) -> ChannelRoleOverride:
        """|coro|

        Create a role-based permission override in this channel.

        Parameters
        -----------
        role: :class:`.Role`
            The role to create an override for.
        override: :class:`.PermissionOverride`
            The override values to use.

        Returns
        --------
        :class:`.ChannelRoleOverride`
            The created role override.
        """

        data = await self._platform.create_channel_role_override(
            self,
            role.id,
            permissions=override.to_dict(),
        )
        return ChannelRoleOverride(data=data, server=self.server)

    async def fetch_role_override(self, role: Role) -> ChannelRoleOverride:
        """|coro|

        Fetch a role-based permission override in this channel.

        Parameters
        -----------
        role: :class:`.Role`
            The role whose override to fetch.

        Returns
        --------
        :class:`.ChannelRoleOverride`
            The role override.
        """

        data = await self._platform.get_channel_role_override(
            self,
            role.id,
        )
        return ChannelRoleOverride(data=data, server=self.server)

    async def fetch_role_overrides(self) -> List[ChannelRoleOverride]:
        """|coro|

        Fetch all role-based permission overrides in this channel.

        Returns
        --------
        List[:class:`.ChannelRoleOverride`]
            The role overrides.
        """

        data = await self._platform.get_channel_role_overrides(self.server_id, self.id)
        return [
            ChannelRoleOverride(data=override_data, server=self.server)
            for override_data in data
        ]

    async def update_role_override(self, role: Role, override: PermissionOverride) -> ChannelRoleOverride:
        """|coro|

        Update a role-based permission override in this channel.

        Parameters
        -----------
        role: :class:`.Role`
            The role to update an override for.
        override: :class:`.PermissionOverride`
            The new override values to use.

        Returns
        --------
        :class:`.ChannelRoleOverride`
            The updated role override.
        """

        data = await self._platform.update_channel_role_override(
            self,
            role.id,
            permissions=override.to_dict(),
        )
        return ChannelRoleOverride(data=data, server=self.server)

    async def delete_role_override(self, role: Role) -> None:
        """|coro|

        Delete a role-based permission override in this channel.

        Parameters
        -----------
        role: :class:`.Role`
            The role whose override to delete.
        """

        await self._platform.delete_channel_role_override(
            self,
            role.id,
        )

    async def create_user_override(self, user: Member, override: PermissionOverride) -> ChannelUserOverride:
        """|coro|

        Create a user-based permission override in this channel.

        Parameters
        -----------
        user: :class:`.Member`
            The member to create an override for.
        override: :class:`.PermissionOverride`
            The override values to use.

        Returns
        --------
        :class:`.ChannelUserOverride`
            The created role override.
        """

        data = await self._platform.create_channel_user_override(
            self,
            user.id,
            permissions=override.to_dict(),
        )
        return ChannelUserOverride(data=data, server=self.server)

    async def fetch_user_override(self, user: Member) -> ChannelUserOverride:
        """|coro|

        Fetch a user-based permission override in this channel.

        Parameters
        -----------
        user: :class:`.Member`
            The member whose override to fetch.

        Returns
        --------
        :class:`.ChannelUserOverride`
            The role override.
        """

        data = await self._platform.get_channel_user_override(
            self,
            user.id,
        )
        return ChannelUserOverride(data=data, server=self.server)

    async def fetch_user_overrides(self) -> List[ChannelUserOverride]:
        """|coro|

        Fetch all user-based permission overrides in this channel.

        Returns
        --------
        List[:class:`.ChannelUserOverride`]
            The role overrides.
        """

        data = await self._platform.get_channel_user_overrides(self)
        return [
            ChannelUserOverride(data=override_data, server=self.server)
            for override_data in data
        ]

    async def update_user_override(self, user: Member, override: PermissionOverride) -> ChannelUserOverride:
        """|coro|

        Update a user-based permission override in this channel.

        Parameters
        -----------
        user: :class:`.Member`
            The member to update an override for.
        override: :class:`.PermissionOverride`
            The new override values to use.

        Returns
        --------
        :class:`.ChannelUserOverride`
            The updated role override.
        """

        data = await self._platform.update_channel_user_override(
            self,
            user.id,
            permissions=override.to_dict(),
        )
        return ChannelUserOverride(data=data, server=self.server)

    async def delete_user_override(self, user: Member) -> None:
        """|coro|

        Delete a user-based permission override in this channel.

        Parameters
        -----------
        user: :class:`.Member`
            The member whose override to delete.
        """

        await self._platform.delete_channel_user_override(
            self,
            user.id,
        )
    
    async def delete(self) -> None:
        """|coro|
        
        Delete this channel.
        """
        await self._platform.delete_channel(self.server_id, self.id)
    
    async def archive(self) -> None:
        """|coro|
        
        Archive this channel.
        """
        await self._platform.archive_channel(self.server_id, self.id)
    
    async def restore(self) -> None:
        """|coro|
        
        Restore this channel from its archived state.
        """
        await self._platform.restore_channel(self.server_id, self.id)

GuildChannel = ServerChannel # discord.py

class Reply(Hashable, HasContentMixin, metaclass=abc.ABCMeta):
    """
    An ABC for replies to posts.

    .. container:: operations

        .. describe:: x == y

            Checks if two replies are equal.

        .. describe:: x != y

            Checks if two replies are not equal.

        .. describe:: hash(x)

            Returns the reply's hash.
    
    Attributes
    -----------
    id: :class:`int`
        The reply's ID.
    content: :class:`str`
        The reply's content.
    created_at: :class:`datetime.datetime`
        When the reply was created.
    updated_at: Optional[:class:`datetime.datetime`]
        When the reply was last updated.
    """
    __slots__ = (
        'id',
        'content',
        '_mentions',
        'author_id',
        'created_at',
        'updated_at',
        'channel_id',
        'replied_to_id',
        'replied_to_author_id',
        '_state',
    )

    def __init__(self, *, state, _platform, data: ContentComment):
        super().__init__()
        self._state = state
        self._platform = _platform or platform
        self.channel_id: str = data.get('channelId')

        self.id: int = int(data['id'])
        self.content: str = data['content']
        self._mentions = self._create_mentions(data.get('mentions'))
        self._extract_attachments(self.content)

        self.author_id: str = data.get('createdBy')
        self.created_at: datetime.datetime = data.get('createdAt')
        self.updated_at: Optional[datetime.datetime] = data.get('updatedAt')

        self.replied_to_id: Optional[int] = None
        self.replied_to_author_id: Optional[str] = None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} author={self.author!r}>'

    @property
    def _content_type(self) -> str:
        return getattr(self.channel, 'content_type', self.channel.type.value)

    @property
    def author(self) -> Optional[Member]:
        """Optional[:class:`.Member`]: The :class:`.Member` that created the
        reply, if they are cached."""
        return self.server.get_member(self.author_id)

    @property
    def channel(self) -> ServerChannel:
        """:class:`~.abc.ServerChannel`: The channel that the reply is in."""
        return self.parent.channel

    @property
    def group(self) -> Group:
        """:class:`~agnostica.Group`: The group that the reply is in."""
        return self.parent.group

    @property
    def server(self) -> Server:
        """:class:`.Server`: The server that the reply is in."""
        return self.parent.server

    @classmethod
    def _copy(cls, reply):
        self = cls.__new__(cls)

        self.parent = reply.parent
        self.parent_id = reply.parent_id
        self.id = reply.id
        self.content = reply.content
        self.author_id = reply.author_id
        self.created_at = reply.created_at
        self.updated_at = reply.updated_at
        self.replied_to_id = reply.replied_to_id
        self.replied_to_author_id = reply.replied_to_author_id

        return self

    def _update(self, data: ContentComment) -> None:
        try:
            self.content = data['content']
        except KeyError:
            pass

        try:
            self.updated_at = data['updatedAt']
        except KeyError:
            pass