"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Optional

from .asset import AssetMixin, Asset
from .errors import InvalidArgument
from .mixins import Hashable
from .user import Member

if TYPE_CHECKING:
    from .types.emote import Emote as EmotePayload


__all__ = (
    'Emoji',
    'Emote',
)


class Emote(Hashable, AssetMixin):
    """Represents an emote on a platform.

    .. container:: operations

        .. describe:: x == y

            Checks if two emotes are equal.

        .. describe:: x != y

            Checks if two emotes are not equal.

        .. describe:: hash(x)

            Returns the emote's hash.

        .. describe:: str(x)

            Returns the name of the emote.

    Attributes
    -----------
    id: :class:`int`
        The emote's ID.
    name: :class:`str`
        The emote's name.
    server_id: Optional[:class:`str`]
        The ID of the server that the emote is from, if any.
    """

    def __init__(self, *, state, data: EmotePayload, **extra):
        self._state = state
        self._server = extra.get('server')

        self.id: int = data.get('id')
        self.name: str = data.get('name') or ''
        self.server_id: Optional[str] = data.get('serverId') or data.get('teamId')
        self.author_id: Optional[str] = data.get('createdBy')
        self.created_at: Optional[datetime.datetime] = data.get('createdAt')

        self._animated: bool = data.get('isAnimated', False)
        self.aliases: List[str] = data.get('aliases', [])

        self._underlying: Asset = data.get('asset')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Emote id={self.id!r} name={self.name!r} server={self.server!r}>'

    @property
    def author(self) -> Optional[Member]:
        """Optional[:class:`.Member`]: The :class:`.Member` who created the custom emote, if any."""
        return self.server.get_member(self.author_id)

    @property
    def server(self):
        """Optional[:class:`.Server`]: The server that the emote is from, if any."""
        return self._server or self._state._get_server(self.server_id)

    @property
    def guild(self):
        """Optional[:class:`.Server`]: |dpyattr|

        This is an alias of :attr:`.server`.

        The server that the emote is from, if any.
        """
        return self.server

    @property
    def animated(self) -> bool:
        """:class:`bool`: Whether the emote is animated."""
        return self._underlying.is_animated()

    @property
    def url(self) -> str:
        """:class:`str`: The emote's CDN URL."""
        return self._underlying.url

    def url_with_format(self, format: str) -> str:
        """Returns a new URL with a different format. By default, the format
        will be ``apng`` if provided, else ``webp``.

        This is functionally a more restricted version of :meth:`Asset.with_format`;
        that is, only formats that are available to emotes can be used in an
        attempt to avoid generating nonfunctional URLs.

        Parameters
        -----------
        format: :class:`str`
            The new format to change it to. Must be
            'png' or 'webp'

        Returns
        --------
        :class:`str`
            The emote's newly updated CDN URL.

        Raises
        -------
        InvalidArgument
            Invalid format provided.
        """

        valid_formats = ['png', 'webp']


        if format not in valid_formats:
            raise InvalidArgument(f'format must be one of {valid_formats}')

        return self._underlying.with_format(format).url

    def url_with_static_format(self, format: str) -> str:
        """Returns a new URL with a different format if the emote is static,
        else the current (animated) URL is returned.

        This is functionally a more restricted version of :meth:`Asset.with_static_format`;
        that is, only formats that are available to emotes can be used in an
        attempt to avoid generating nonfunctional URLs.

        Parameters
        -----------
        format: :class:`str`
            The new format to change it to. Must be one of 'png' or 'webp'.

        Returns
        --------
        :class:`str`
            The emote's newly updated CDN URL.

        Raises
        -------
        InvalidArgument
            Invalid format provided.
        """

        valid_formats = ['png', 'webp']

        if format not in valid_formats:
            raise InvalidArgument(f'format must be one of {valid_formats}')

        return self._underlying.with_static_format(format).url

Emoji = Emote