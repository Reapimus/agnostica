"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from typing import Any, Dict, List, Optional, Tuple, Union

from .file import Attachment
from .http import HTTPClientBase
from .user import User, Member
from .abc import ServerChannel
from .errors import HTTPException
from .enums import FileType
from .utils import valid_video_extensions
from .embed import Embed
from .role import Role
from .server import Server

import re

class EqualityComparable:
    __slots__ = ()

    id: Union[str, int]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return other.id == self.id
        return NotImplemented

class Hashable(EqualityComparable):
    __slots__ = ()

    def __hash__(self) -> int:
        return hash(self.id)

class Mentions:
    """Represents mentions in message content. This data is determined and
    sent by the platform rather than being parsed by the library.

    In case the platform does not provide this data, it may be provided by
    the adapter or the library will attempt to identify common mention patterns
    in the content.

    Attributes
    -----------
    everyone: :class:`bool`
        Whether ``@everyone`` was mentioned.
    here: :class:`bool`
        Whether ``@here`` was mentioned.
    """

    def __init__(self, *, state: HTTPClientBase, server: Server, data: Optional[dict]):
        self._state = state
        self._server = server
        self._users = data.get('users') or []
        self._channels = data.get('channels') or []
        self._roles = data.get('roles') or []

        self.everyone = data.get('everyone', False)
        self.here = data.get('here', False)

    def __repr__(self) -> str:
        return f'<Mentions users={len(self._users)} channels={len(self._channels)} roles={len(self._roles)} everyone={self.everyone} here={self.here}>'

    @property
    def users(self) -> List[Union[Member, User]]:
        """List[Union[:class:`.Member`, :class:`~guilded.User`]]: The list of users who were mentioned."""
        users = []
        for user_data in self._users:
            user = self._state._get_user(user_data['id'])
            if self._server:
                user = self._state._get_server_member(self._server.id, user_data['id']) or user
            if user:
                users.append(user)

        return users

    @property
    def channels(self) -> List[ServerChannel]:
        """List[:class:`~.abc.ServerChannel`]: The list of channels that were mentioned.

        An empty list is always returned in a DM context.
        """
        if not self._server:
            return []

        channels = []
        for channel_data in self._channels:
            channel = self._state._get_server_channel_or_thread(self._server.id, channel_data['id'])
            if channel:
                channels.append(channel)

        return channels

    @property
    def roles(self) -> List[Role]:
        """List[:class:`.Role`]: The list of roles that were mentioned.

        An empty list is always returned in a DM context.
        """
        if not self._server:
            return []

        roles = []
        for role_data in self._roles:
            role = self._server.get_role(role_data['id'])
            if role:
                roles.append(role)

        return roles

    async def fill(
        self,
        *,
        ignore_cache: bool = False,
        ignore_errors: bool = False,
    ) -> None:
        """|coro|

        Fetch & fill the internal cache with the targets referenced.

        Parameters
        -----------
        ignore_cache: :class:`bool`
            Whether to fetch objects even if they are already cached.
            Defaults to ``False`` if not specified.
        ignore_errors: :class:`bool`
            Whether to ignore :exc:`HTTPException`\s that occur while fetching.
            Defaults to ``False`` if not specified.
        """
        # Bots cannot fetch any role information so they are not handled here.

        # Just fetch the whole member list instead of fetching >=5 members individually.
        uncached_user_count = len(self._users) - len(self.users)
        if (
            self._server and (
                uncached_user_count >= 5
                or (len(self._users) >= 5 and ignore_cache)
            )
        ):
            # `fill_members` here would cause potentially unwanted/unexpected
            # cache usage, especially in large servers.
            members = await self._server.fetch_members()
            user_ids = [user['id'] for user in self._users]
            for member in members:
                if member.id in user_ids:
                    self._state.add_to_member_cache(member)

        else:
            for user_data in self._users:
                cached_user = self._state._get_user(user_data['id'])
                if self._server:
                    cached_user = self._state._get_server_member(self._server.id, user_data['id']) or cached_user

                if ignore_cache or not cached_user:
                    if self._server:
                        try:
                            user = await self._server.fetch_member(user_data['id'])
                        except HTTPException:
                            if not ignore_errors:
                                raise
                        else:
                            self._state.add_to_member_cache(user)
                    else:
                        try:
                            user = await self._state.get_user(user_data['id'])
                        except HTTPException:
                            if not ignore_errors:
                                raise
                        else:
                            self._state.add_to_user_cache(user)

        # Just fetch the whole role list instead of fetching >=5 roles individually.
        uncached_role_count = len(self._roles) - len(self.roles)
        if (
            self._server and (
                uncached_role_count >= 5
                or (len(self._roles) >= 5 and ignore_cache)
            )
        ):
            # `fill_roles` here would cause potentially unwanted/unexpected
            # cache usage, especially in large servers.
            roles = await self._server.fetch_roles()
            role_ids = [role['id'] for role in self._roles]
            for role in roles:
                if role.id in role_ids:
                    self._state.add_to_role_cache(role)

        else:
            for role_data in self._roles:
                cached_role = self._state._get_server_role(self._server.id, role_data['id'])
                if self._server and (ignore_cache or not cached_role):
                    try:
                        role = await self._server.fetch_role(role_data['id'])
                    except HTTPException:
                        if not ignore_errors:
                            raise
                    else:
                        self._state.add_to_role_cache(role)

        for channel_data in self._channels:
            if not self._server:
                # This should never happen
                break

            cached_channel = self._state._get_server_channel_or_thread(self._server.id, channel_data['id'])
            if ignore_cache or not cached_channel:
                try:
                    channel = await self._server.fetch_channel(channel_data['id'])
                except HTTPException:
                    if not ignore_errors:
                        raise
                else:
                    self._state.add_to_server_channel_cache(channel)

class HasContentMixin:
    def __init__(self):
        self.emotes: list = []
        self._raw_user_mentions: list = []
        self._raw_channel_mentions: list = []
        self._raw_role_mentions: list = []
        self._user_mentions: list = []
        self._channel_mentions: list = []
        self._role_mentions: list = []
        self._mentions_everyone: bool = False
        self._mentions_here: bool = False
        self.embeds: List[Embed] = []
        self.attachments: List[Attachment] = []

    @property
    def user_mentions(self) -> List[Union[Member, User]]:
        """List[Union[:class:`~agnostica.Member`, :class:`~agnostica.User`]]: The list of users who are mentioned in the content."""
        if hasattr(self, '_mentions'):
            return self._mentions.users
        return self._user_mentions

    @property
    def raw_user_mentions(self) -> List[str]:
        """List[:class:`str`]: A list of user IDs for the users that are
        mentioned in the content.

        This is useful if you need the users that are mentioned but do not
        care about their resolved data.
        """
        if hasattr(self, '_mentions'):
            return [obj['id'] for obj in self._mentions._users]
        return self._raw_user_mentions

    @property
    def mentions(self) -> List[Union[Member, User]]:
        """List[Union[:class:`~agnostica.Member`, :class:`~agnostica.User`]]:

        The list of users who are mentioned in the content.
        """
        return self.user_mentions

    @property
    def raw_mentions(self) -> List[str]:
        """List[:class:`str`]:

        A list of user IDs for the users that are mentioned in the content.

        This is useful if you need the users that are mentioned but do not
        care about their resolved data.
        """
        return self.raw_user_mentions

    @property
    def channel_mentions(self) -> List[ServerChannel]:
        """List[:class:`~.abc.ServerChannel`]: The list of channels that are
        mentioned in the content."""
        if hasattr(self, '_mentions'):
            return self._mentions.channels
        return self._channel_mentions

    @property
    def raw_channel_mentions(self) -> List[str]:
        """List[:class:`str`]: A list of channel IDs for the channels that are
        mentioned in the content.

        This is useful if you need the channels that are mentioned but do not
        care about their resolved data.
        """
        if hasattr(self, '_mentions'):
            return [obj['id'] for obj in self._mentions._channels]
        return self._raw_channel_mentions

    @property
    def role_mentions(self) -> List[Role]:
        """List[:class:`.Role`]: The list of roles that are mentioned in the content."""
        if hasattr(self, '_mentions'):
            return self._mentions.roles
        return self._role_mentions

    @property
    def raw_role_mentions(self) -> List[int]:
        """List[:class:`int`]: A list of role IDs for the roles that are
        mentioned in the content.

        This is useful if you need the roles that are mentioned but do not
        care about their resolved data.
        """
        if hasattr(self, '_mentions'):
            return [obj['id'] for obj in self._mentions._roles]
        return self._raw_role_mentions

    @property
    def mention_everyone(self) -> bool:
        """:class:`bool`: Whether the content mentions ``@everyone``\."""
        if hasattr(self, '_mentions'):
            return self._mentions.everyone
        return self._mentions_everyone

    @property
    def mention_here(self) -> bool:
        """:class:`bool`: Whether the content mentions ``@here``\."""
        if hasattr(self, '_mentions'):
            return self._mentions.here
        return self._mentions_here
    
    def _get_full_content(self, data: Dict[str, Any]) -> str:
        if self._platform.get_full_content is None:
            raise NotImplementedError('Received none-string content data from adapter but adapter has not implemented _get_full_content!')
        return self._platform.get_full_content(data) or ''

    def _create_mentions(self, data: Optional[Dict[str, Any]]) -> Mentions:
        # This will always be called after setting _state and _server/server_id so this should be safe
        mentions = Mentions(state=self._state, _platform=self._platform, server=self.server, data=data or {})
        return mentions

    def _extract_attachments(self, content: str) -> None:
        if content is None:
            content = ''
        elif not isinstance(content, str):
            raise TypeError(f'expected str for content, not {content.__class__.__name__}')

        self.attachments.clear()

        if self._platform.ATTACHMENT_REGEX != '':
            matches: List[Tuple[str, str, str]] = re.findall(self._platform.ATTACHMENT_REGEX, content)
            for match in matches:
                caption, url, extension = match
                attachment = Attachment(
                    state=self._state,
                    data={
                        'type': FileType.video if extension in valid_video_extensions else FileType.image,
                        'caption': caption or None,
                        'url': url,
                    },
                )
                self.attachments.append(attachment)