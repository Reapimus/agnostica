"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations

import asyncio
import datetime
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, List, Sequence, Union

from .embed import Embed
from .enums import ChannelVisibility, try_enum, MessageType
from .errors import HTTPException
from .mixins import Hashable, HasContentMixin
from .utils import MISSING
from .globals import platform

if TYPE_CHECKING:
    from .types.channel import Mentions as MentionsPayload

    from .abc import Messageable, User as abc_User
    from .channel import Thread
    from .emote import Emote
    from .group import Group
    from .role import Role
    from .server import Server
    from .user import Member, User

log = logging.getLogger(__name__)

class ChatMessage(Hashable, HasContentMixin):
    """A message on a platform.

    There is an alias for this class called ``Message``.

    .. container:: operations

        .. describe:: x == y

            Checks if two messages are equal.

        .. describe:: x != y

            Checks if two messages are not equal.

        .. describe:: hash(x)

            Returns the message's hash.

    Attributes
    -----------
    id: :class:`str`
        The message's ID.
    content: :class:`str`
        The text content of the message.
    embeds: List[:class:`.Embed`]
        The list of embeds in the message.
        This does not include link unfurl embeds.
    attachments: List[:class:`.Attachment`]
        The list of media attachments in the message.
    channel: :class:`~.abc.ServerChannel`
        The channel this message was sent in.
    webhook_id: Optional[:class:`str`]
        The webhook's ID that sent the message, if applicable.
    replied_to_ids: List[:class:`str`]
        A list of message IDs that the message replied to, up to 5.
    private: :class:`bool`
        Whether the message was sent so that only server moderators and users
        mentioned in the message can see it.
    silent: :class:`bool`
        Whether the message was sent silently, i.e., if this is true then
        users mentioned in the message were not sent a notification.
    pinned: :class:`bool`
        Whether the message is pinned in its channel.
    hidden_preview_urls: List[:class:`str`]
        URLs in ``content`` that have been prevented from unfurling as a link
        preview when displayed on the platform.
    created_at: :class:`datetime.datetime`
        When the message was created.
    updated_at: Optional[:class:`datetime.datetime`]
        When the message was last updated.
    deleted_at: Optional[:class:`datetime.datetime`]
        When the message was deleted.
    """

    __slots__ = (
        '_state',
        'channel',
        'channel_id',
        'server_id',
        'group_id',
        'id',
        'type',
        'webhook_id',
        'author_id',
        'created_at',
        'updated_at',
        'deleted_at',
        'replied_to_ids',
        'silent',
        'private',
        'pinned',
        'content',
        'embeds',
        'hidden_preview_urls',
    )

    def __init__(self, *, state, _platform, channel: Messageable, data, **extra: Any):
        super().__init__()
        self._platform = _platform or platform
        self._state = state
        data = data.get('message', data)

        self.channel = channel
        self._author = extra.get('author')
        self._webhook = extra.get('webhook')

        self.channel_id: str = data.get('channelId')
        self.server_id: str = data.get('serverId') or data.get('teamId')
        self.group_id: Optional[str] = data.get('groupId')

        self.id: str = data['id']
        self.type: MessageType = try_enum(MessageType, data.get('type'))

        self.replied_to_ids: List[str] = data.get('replyMessageIds') or data.get('repliesToIds') or []
        self.author_id: str = data.get('createdBy')
        self.webhook_id: Optional[str] = data.get('createdByWebhookId') or data.get('webhookId')
        self._webhook_username: Optional[str] = None
        self._webhook_avatar_url: Optional[str] = None
        self.hidden_preview_urls: List[str] = data.get('hiddenLinkPreviewUrls') or []

        self.created_at: datetime.datetime = data.get('createdAt')
        self.updated_at: Optional[datetime.datetime] = data.get('updatedAt') or data.get('editedAt')
        self.deleted_at: Optional[datetime.datetime] = data.get('deletedAt')

        self.silent: bool = data.get('isSilent') or False
        self.private: bool = data.get('isPrivate') or False
        self.pinned: bool = data.get('isPinned') or False

        if isinstance(data.get('content'), dict):
            # Webhook execution responses
            self.content: str = self._get_full_content(data['content'])
            hidden_embed_urls: Optional[Dict[str, bool]] = data['content'].get('document', {}).get('data', {}).get('hiddenEmbedUrls')
            if hidden_embed_urls:
                self.hidden_preview_urls = [key for [key, value] in hidden_embed_urls.items() if value]

            profile: Optional[Dict[str, str]] = data['content'].get('document', {}).get('data', {}).get('profile')
            if profile:
                self._webhook_username = profile.get('name')
                self._webhook_avatar_url = profile.get('profilePicture')

        else:
            self.content: str = data.get('content') or ''
            self._mentions = self._create_mentions(data.get('mentions'))
            self.embeds: List[Embed] = [
                Embed.from_dict(embed) for embed in (data.get('embeds') or [])
            ]
            self._extract_attachments(self.content)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} author={self.author!r} channel={self.channel!r}>'

    @property
    def server(self) -> Server:
        """Optional[:class:`.Server`]: The server this message was sent in."""
        return self._state._get_server(self.server_id)

    @property
    def guild(self) -> Server:
        """Optional[:class:`.Server`]:

        This is an alias of :attr:`.server`.

        The server this message was sent in.
        """
        return self.server

    @property
    def group(self) -> Group:
        """Optional[:class:`.Group`]: The group that the message is in."""
        return self.channel.group

    @property
    def author(self) -> Optional[Union[Member, User]]:
        """Optional[Union[:class:`.Member`, :class:`~agnostica.User`]]: The user that created this message, if they are cached."""
        if self._author:
            return self._author

        user = None
        if self.server:
            user = self.server.get_member(self.author_id)

        if not user:
            user = self._state._get_user(self.author_id)

        if self.webhook_id or self._webhook:
            data = {
                'id': self.author_id,
                'type': 'bot',
            }
            # FIll in webhook defaults if available & then profile overrides if available
            if self._webhook:
                data['name'] = self._webhook.name
                data['profilePicture'] = self._webhook.avatar.url if self._webhook.avatar else None
            if self._webhook_username:
                data['name'] = self._webhook_username
            if self._webhook_avatar_url:
                data['profilePicture'] = self._webhook_avatar_url

            user = self._state.create_user(data=data)

        return user

    @property
    def created_by_bot(self) -> bool:
        """:class:`bool`: Whether this message's author is a bot or webhook."""
        return self.author.bot if self.author else self.webhook_id is not None

    @property
    def share_url(self) -> str:
        """:class:`str`: The share URL of the message."""
        if self.channel:
            if self._platform.get_message_share_url is not None:
                return self._platform.get_message_share_url(self)
            return f'{self.channel.share_url}?messageId={self.id}'
        return None

    @property
    def jump_url(self) -> str:
        """:class:`str`:

        This is an alias of :attr:`.share_url`.

        The share URL of the message.
        """
        return self.share_url

    @property
    def replied_to(self) -> List[ChatMessage]:
        """List[:class:`.ChatMessage`]: The list of messages that the message replied to.

        This property relies on message cache. If you need a list of IDs,
        consider :attr:`.replied_to_ids` instead.
        """
        messages = [self._state._get_message(message_id) for message_id in self.replied_to_ids]
        return [m for m in messages if m is not None]

    async def delete(self, *, delay: Optional[float] = None) -> None:
        """|coro|

        Delete this message.

        Parameters
        -----------
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait in the background before
            deleting this message. If the deletion fails, then it is silently ignored.

        Raises
        -------
        Forbidden
            You do not have proper permissions to delete this message.
        NotFound
            This message has already been deleted.
        HTTPException
            Deleting this message failed.
        """

        coro = self._platform.delete_channel_message(self.server_id, self.channel_id, self.id)

        if delay is not None:

            async def delete(delay: float):
                await asyncio.sleep(delay)
                try:
                    await coro
                except HTTPException:
                    pass

            asyncio.create_task(delete(delay))

        else:
            await coro

    async def edit(
        self,
        content: Optional[str] = MISSING,
        *,
        embed: Optional[Embed] = MISSING,
        embeds: Optional[Sequence[Embed]] = MISSING,
        hide_preview_urls: Optional[Sequence[str]] = MISSING,
    ) -> ChatMessage:
        """|coro|

        Edit this message.

        .. warning::

            This method **overwrites** all content previously in the message
            using the new payload.

        Parameters
        -----------
        content: :class:`str`
            The text content of the message.
        embed: :class:`.Embed`
            An embed in the message.
            This parameter cannot be meaningfully combined with ``embeds``.
        embeds: List[:class:`.Embed`]
            A list of embeds in the message.
            At present, this can contain at most 1 value.
            This parameter cannot be meaningfully combined with ``embed``.
        hide_preview_urls: List[:class:`str`]
            URLs in ``content`` to prevent unfurling as a link preview when displaying on the platform.

        Returns
        --------
        :class:`.ChatMessage`
            The edited message.

        Raises
        -------
        NotFound
            The message does not exist.
        Forbidden
            The message is not owned by you or it is in a channel you cannot access.
        HTTPException
            Could not edit the message.
        """

        from .http import handle_message_parameters

        params = handle_message_parameters(
            content=content,
            embed=embed,
            embeds=embeds,
            hide_preview_urls=hide_preview_urls,
        )

        data = await self._platform.update_channel_message(
            self.channel_id,
            self.id,
            payload=params.payload,
        )

        message = self._state.create_message(
            data=data,
            channel=self.channel,
        )

        return message

    async def add_reaction(self, emote: Emote, /) -> None:
        """|coro|

        Add a reaction to this message.

        Parameters
        -----------
        emote: :class:`.Emote`
            The emote to add.
        """
        emote_id: int = getattr(emote, 'id', emote)
        await self._state.add_channel_message_reaction(self.channel_id, self.id, emote_id)

    async def remove_reaction(self, emote: Emote, member: Optional[abc_User] = None) -> None:
        """|coro|

        Remove a reaction from this message.

        If the reaction is not your own then :attr:`~Permissions.manage_messages` is required.

        Parameters
        -----------
        emote: :class:`.Emote`
            The emote to remove.
        member: Optional[:class:`~.abc.User`]
            The member whose reaction to remove.
            If this is not specified, the client's reaction will be removed instead.
        """
        emote_id: int = getattr(emote, 'id', emote)
        await self._platform.remove_channel_message_reaction(self.channel.id, self.id, emote_id, member.id if member else None)

    async def remove_self_reaction(self, emote: Emote, /) -> None:
        """|coro|

        Remove one of your reactions from this message.
            Use :meth:`.remove_reaction` instead.

        Parameters
        -----------
        emote: :class:`.Emote`
            The emote to remove.
        """
        await self.remove_reaction(emote)

    async def clear_reaction(self, emote: Emote, /) -> None:
        """|coro|

        Bulk remove reactions from this message based on their emote.

        To remove individual reactions from specific users, see :meth:`.remove_reaction`.

        Parameters
        -----------
        emote: :class:`.Emote`
            The emote to remove.
        """
        emote_id: int = getattr(emote, 'id', emote)
        await self._platform.remove_channel_message_reactions(self.channel.id, self.id, emote_id)

    async def clear_reactions(self) -> None:
        """|coro|

        Bulk remove all the reactions from this message.
        """
        await self._platform.remove_channel_message_reactions(self.channel.id, self.id)

    async def reply(
        self,
        content: Optional[str] = MISSING,
        *,
        embed: Optional[Embed] = MISSING,
        embeds: Optional[Sequence[Embed]] = MISSING,
        reference: Optional[ChatMessage] = MISSING,
        reply_to: Optional[Sequence[ChatMessage]] = MISSING,
        mention_author: Optional[bool] = None,
        silent: Optional[bool] = None,
        private: bool = False,
        delete_after: Optional[float] = None,
    ) -> ChatMessage:
        """|coro|

        Reply to this message.
        This is identical to :meth:`abc.Messageable.send`, but the
        ``reply_to`` parameter already includes this message.
        """

        reply_to = reply_to if reply_to is not MISSING else []
        if self not in reply_to:
            # We don't have a say in where the message appears in the reply
            # list unfortunately; it is always sorted chronologically.
            reply_to.append(self)

        return await self.channel.send(
            content=content,
            embed=embed,
            embeds=embeds,
            reference=reference,
            reply_to=reply_to,
            mention_author=mention_author,
            silent=silent,
            private=private,
            delete_after=delete_after,
        )

    async def create_thread(self, name: str, *, visibility: ChannelVisibility = None) -> Thread:
        """|coro|

        Create a new thread under the message.

        .. warning::

            Be careful with this method!
            It is very easy to accidentally cause a loop if you create a
            thread on a message that caused the creation of its thread.

        Depending on the type of the parent channel, this method requires
        different permissions:

        +------------------------------+-----------------------------------+
        |         Parent Type          |             Permission            |
        +------------------------------+-----------------------------------+
        | :attr:`~.ChannelType.chat`   | :attr:`Permissions.read_messages` |
        +------------------------------+-----------------------------------+
        | :attr:`~.ChannelType.voice`  | :attr:`Permissions.hear_voice`    |
        +------------------------------+-----------------------------------+
        | :attr:`~.ChannelType.stream` | :attr:`Permissions.view_streams`  |
        +------------------------------+-----------------------------------+

        Parameters
        -----------
        name: :class:`str`
            The thread's name. Can include spaces.
        visibility: Optional[:class:`.ChannelVisibility`]
            What users can access the channel. Currently, this can only be
            :attr:`~.ChannelVisibility.private` or ``None``.

        Returns
        --------
        :class:`.Thread`
            The created thread.

        Raises
        -------
        NotFound
            The server, channel, or message does not exist.
        Forbidden
            You are not allowed to create a thread in this channel.
        HTTPException
            Failed to create a thread.
        """
        return await self.channel.create_thread(name=name, message=self, visibility=visibility)

    async def pin(self) -> None:
        """|coro|

        Pin this message.

        Raises
        -------
        NotFound
            The channel or message does not exist.
        Forbidden
            You are not allowed to pin messages in this channel.
        HTTPException
            Failed to pin the message.
        """
        await self._platform.pin_channel_message(self.channel.id, self.id)

    async def unpin(self) -> None:
        """|coro|

        Unpin this message.

        Raises
        -------
        NotFound
            The channel or message does not exist.
        Forbidden
            You are not allowed to unpin messages in this channel.
        HTTPException
            Failed to unpin the message.
        """
        await self._platform.unpin_channel_message(self.channel.id, self.id)

Message = ChatMessage