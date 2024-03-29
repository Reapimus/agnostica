"""This file contains code from guilded.py, see LICENSE.txt for full license details."""
from agnostica.enums import Enum

class FlowTriggerType(Enum):
    server_updated = 'TeamAuditLogTeamUpdated'
    member_muted = 'TeamAuditLogMemberMuted'
    member_sent_message_to_channel = 'BotTriggerSendMessageToTeamChannel'
    member_joined = 'BotTriggerMemberJoined'
    application_received = 'TeamAuditLogApplicationReceived'
    toggle_list_item = 'BotTriggerChangeListItemState'
    event_created = 'BotTriggerCalendarEventCreated'
    event_updated = 'BotTriggerCalendarEventUpdated'
    event_removed = 'BotTriggerCalendarEventDeleted'
    forum_topic_created = 'BotTriggerForumTopicCreated'
    forum_topic_updated = 'BotTriggerForumTopicUpdated'
    forum_topic_deleted = 'BotTriggerForumTopicDeleted'
    list_item_created = 'BotTriggerListItemCreated'
    list_item_updated = 'BotTriggerListItemUpdated'
    list_item_deleted = 'BotTriggerListItemDeleted'
    doc_created = 'BotTriggerDocCreated'
    doc_updated = 'BotTriggerDocUpdated'
    doc_deleted = 'BotTriggerDocDeleted'
    media_created = 'BotTriggerMediaCreated'
    media_updated = 'BotTriggerMediaUpdated'
    media_deleted = 'BotTriggerMediaDeleted'
    announcement_created = 'BotTriggerAnnouncementCreated'
    announcement_updated = 'BotTriggerAnnouncementUpdated'
    announcement_deleted = 'BotTriggerAnnouncementDeleted'
    voice_group_joined = 'BotTriggerVoiceChannelGroupJoined'
    voice_group_left = 'BotTriggerVoiceChannelGroupLeft'
    twitch_stream_online = 'BotTriggerTwitchStreamOnline'
    twitch_stream_offline = 'BotTriggerTwitchStreamOffline'
    twitch_stream_subscribed = 'BotTriggerTwitchStreamSubscribed'
    twitch_stream_followed = 'BotTriggerTwitchStreamFollowed'
    twitch_stream_unfollowed = 'BotTriggerTwitchStreamUnfollowed'
    twitch_stream_unsubscribed = 'BotTriggerTwitchStreamUnsubscribed'
    patreon_tiered_membership_created = 'BotTriggerPatreonTieredMembershipCreated'
    patreon_tiered_membership_updated = 'BotTriggerPatreonTieredMembershipUpdated'
    patreon_tiered_membership_cancelled = 'BotTriggerPatreonTieredMembershipRemoved'
    subscription_created = 'TeamAuditLogServerSubscriptionsSubscriptionCreated'
    subscription_updated = 'BotTriggerServerSubscriptionsSubscriptionUpdated'
    subscription_canceled = 'TeamAuditLogServerSubscriptionsSubscriptionCanceled'
    scheduling_availability_started = 'BotTriggerSchedulingAvailabilityDurationStarted'
    scheduling_availability_ended = 'BotTriggerSchedulingAvailabilityDurationEnded'
    youtube_video_published = 'BotTriggerYoutubeVideoPublished'

class FlowActionType(Enum):
    send_a_custom_message = 'SendMessageToTeamChannel'
    assign_role = 'AssignRoleToMember'
    add_xp_to_member = 'AddTeamXpToMember'
    edit_group_membership = 'EditGroupMembership'
    create_a_forum_topic = 'CreateForumThread'
    create_a_list_item = 'CreateListItem'
    remove_role = 'RemoveRoleFromMember'
    delete_a_message = 'DeleteChannelMessage'
    create_a_doc = 'CreateDoc'

class ServerType(Enum):
    team = 'team'
    organization = 'organization'
    community = 'community'
    clan = 'clan'
    guild = 'guild'
    friends = 'friends'
    streaming = 'streaming'
    other = 'other'

class ServerSubscriptionTierType(Enum):
    gold = 'Gold'
    silver = 'Silver'
    copper = 'Copper'
