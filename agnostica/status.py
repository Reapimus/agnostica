"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .types.user import UserStatus as UserStatusPayload

__all__ = (
    'Status',
)

class Status:
    """Represents a user's status.

    This is displayed under the user's name in the sidebar.

    Attributes
    -----------
    content: Optional[:class:`str`]
        The content of the status.
    emote_id: Optional[:class:`str`]
        The ID of the emote associated with the status.
    """

    __slots__: Tuple[str, ...] = (
        'content',
        'emote_id',
    )

    def __init__(self, *, data: UserStatusPayload):
        self.content = data.get('content')
        self.emote_id = data.get('emoteId')