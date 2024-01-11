"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import List, Literal, TypedDict
from typing_extensions import NotRequired

from .comment import ContentComment
from .channel import Mentions
from .identifier import identifier

class CalendarEventCancellation(TypedDict):
    description: NotRequired[str]
    createdBy: identifier

class CalendarEvent(TypedDict):
    id: identifier
    serverId: identifier
    groupId: identifier
    channelId: identifier
    name: str
    description: NotRequired[str]
    location: NotRequired[str]
    url: NotRequired[str]
    color: NotRequired[int]
    repeats: NotRequired[bool]
    seriesId: NotRequired[str]
    roleIds: NotRequired[List[identifier]]
    isAllDay: NotRequired[bool]
    rsvpLimit: NotRequired[int]
    rsvpDisabled: NotRequired[bool]
    autofillWaitlist: NotRequired[bool]
    startsAt: str
    duration: NotRequired[int]
    isPrivate: NotRequired[bool]
    mentions: NotRequired[Mentions]
    createdAt: str
    createdBy: identifier
    cancellation: NotRequired[CalendarEventCancellation]

class CalendarEventRsvp(TypedDict):
    calendarEventId: identifier
    channelId: NotRequired[identifier]
    serverId: identifier
    userId: identifier
    status: Literal['going', 'maybe', 'declined', 'invited', 'waitlisted', 'not responded']
    createdBy: identifier
    createdAt: str
    updatedBy: NotRequired[identifier]
    updatedAt: NotRequired[str]

class CalendarEventComment(ContentComment):
    calendarEventId: identifier

class RepeatInfoEvery(TypedDict):
    count: int
    interval: Literal['day', 'week', 'month', 'year']

class RepeatInfo(TypedDict):
    type: Literal['once', 'everyDay', 'everyWeek', 'everyMonth', 'custom']
    every: NotRequired[RepeatInfoEvery]
    endsAfterOccurrences: NotRequired[int]
    endDate: NotRequired[str]
    # Weekdays for type == custom and every.interval == week
    on: List[Literal['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']]