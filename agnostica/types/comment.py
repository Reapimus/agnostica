"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from typing import NotRequired, Optional, TypedDict

class ContentComment(TypedDict):
    id: int
    content: str
    createdAt: str
    updatedAt: NotRequired[Optional[str]]
    channelId: str
    createdBy: str