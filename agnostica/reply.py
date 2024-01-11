"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TYPE_CHECKING

from .abc import Reply

if TYPE_CHECKING:
    from .types.announcement import AnnouncementComment
    from .types.calendar_event import CalendarEventComment
    from .types.doc import DocComment
    from .types.forum_topic import ForumTopicComment

    from .channel import Announcement, CalendarEvent, Doc, ForumTopic
    from .emote import Emote

__all__ = (
    'AnnouncementReply',
    'CalendarEventReply',
    'DocReply',
    'ForumTopicReply',
)

class AnnouncementReply(Reply):
    """Represents a reply to an :class:`Announcement`.

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
    parent: :class:`.Announcement`
        The announcement that the reply is a child of.
    parent_id: :class:`int`
        The ID of the parent announcement.
    created_at: :class:`datetime.datetime`
        When the reply was created.
    updated_at: Optional[:class:`datetime.datetime`]
        When the reply was last updated.
    """

    __slots__ = (
        'parent',
        'parent_id',
    )

    def __init__(self, *, state, _platform, data: AnnouncementComment, parent: Announcement):
        self.parent: Announcement = parent
        self.parent_id: str = data.get('announcementId')

        super().__init__(state=state, data=data, _platform=_platform)

    async def edit(
        self,
        *,
        content: str,
    ) -> AnnouncementReply:
        """|coro|

        Edit this reply.

        Parameters
        -----------
        content: :class:`str`
            The content of the reply.

        Returns
        --------
        :class:`AnnouncementReply`
            The updated reply.

        Raises
        -------
        NotFound
            This reply does not exist.
        Forbidden
            You do not have permission to update this reply.
        HTTPException
            Failed to update this reply.
        """

        payload = {
            'content': content,
        }

        data = await self._platform.update_announcement_comment(self, payload=payload)
        return AnnouncementReply(state=self._state, _platform=self._platform, data=data, parent=self.parent)

    async def delete(self) -> None:
        """|coro|

        Delete this reply.

        Raises
        -------
        NotFound
            This reply does not exist.
        Forbidden
            You do not have permission to delete this reply.
        HTTPException
            Failed to delete this reply.
        """

        await self._platform.delete_announcement_comment(self)

    async def add_reaction(self, emote: Emote, /) -> None:
        """|coro|

        Add a reaction to this reply.

        Parameters
        -----------
        emote: :class:`.Emote`
            The emote to add.
        """
        emote_id: int = getattr(emote, 'id', emote)
        await self._platform.add_announcement_comment_reaction(self, emote_id)

    async def remove_self_reaction(self, emote: Emote, /) -> None:
        """|coro|

        Remove one of your reactions from this reply.

        Parameters
        -----------
        emote: :class:`.Emote`
            The emote to remove.
        """
        emote_id: int = getattr(emote, 'id', emote)
        await self._platform.remove_announcement_comment_reaction(self, emote_id)