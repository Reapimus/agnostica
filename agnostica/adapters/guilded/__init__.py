"""This file contains code from guilded.py, see LICENSE.txt for full license details."""

import re
import datetime
from typing import Any, Dict, Optional

import agnostica.abc

from agnostica import PlatformAdapter, Embed, Colour, Attachment, Server, HasContentMixin

from .enums import *
from .asset import *

def ISO8601(string: str):
    if string is None:
        return None

    try:
        return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        try:
            return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
        except:
            # get rid of milliseconds entirely since Guilded may sometimes
            # send a number of digits that datetime.fromisoformat does not
            # accept
            string = re.sub(r'\.\d{1,6}', '', string)
            try:
                return datetime.datetime.fromisoformat(string)
            except:
                pass
        raise TypeError(f'{string} is not a valid ISO8601 datetime.')

class GuildedAdapter(PlatformAdapter):
    _supported_auth_methods = ['token']

    ATTACHMENT_REGEX = re.compile(r'!\[(?P<caption>.+)?\]\((?P<url>https:\/\/(?:s3-us-west-2\.amazonaws\.com\/www\.guilded\.gg|img\.guildedcdn\.com|img2\.guildedcdn\.com|www\.guilded\.gg|cdn\.gilcdn\.com)\/(?:ContentMediaGenericFiles|ContentMedia|WebhookPrimaryMedia)\/[a-zA-Z0-9]+-Full\.(?P<extension>webp|jpeg|jpg|png|gif|apng)(?:\?.+)?)\)')

    GUILDED_EPOCH_DATETIME = datetime.datetime(2016, 1, 1)
    GUILDED_EPOCH_ISO8601 = GUILDED_EPOCH_DATETIME.isoformat() + 'Z'
    GUILDED_EPOCH = int(GUILDED_EPOCH_DATETIME.timestamp())

    DEFAULT_DATE: Optional[datetime.datetime] = GUILDED_EPOCH_DATETIME

    PROFILE_BASE: Optional[str] = 'https://guilded.gg/profile'
    VANITY_BASE: Optional[str] = 'https://guilded.gg/u'

    def get_channel_share_url(self, channel: agnostica.abc.ServerChannel) -> str:
        if channel.server_id is None:
            return f'https://www.guilded.gg/chat/{channel.id}'

        # Using "_" for groups will render weirdly in the client, but the channel contents do appear
        return f'https://www.guilded.gg/teams/{channel.server_id}/groups/{channel.group_id or "_"}/channels/{channel.id}/chat'
    
    def get_server_vanity_url(self, server: Server) -> Optional[str]:
        return f'https://guilded.gg/{server.slug}'
    
    def get_full_content(adapter, self: HasContentMixin, data: Dict[str, Any]):
        try:
            nodes = data['document']['nodes']
        except KeyError:
            # empty message
            return ''

        content = ''
        for node in nodes:
            node_type = node['type']
            if node_type == 'paragraph':
                for element in node['nodes']:
                    if element['object'] == 'text':
                        for leaf in element['leaves']:
                            if not leaf['marks']:
                                content += leaf['text']
                            else:
                                to_mark = '{unmarked_content}'
                                marks = leaf['marks']
                                for mark in marks:
                                    if mark['type'] == 'bold':
                                        to_mark = '**' + to_mark + '**'
                                    elif mark['type'] == 'italic':
                                        to_mark = '*' + to_mark + '*'
                                    elif mark['type'] == 'underline':
                                        to_mark = '__' + to_mark + '__'
                                    elif mark['type'] == 'strikethrough':
                                        to_mark = '~~' + to_mark + '~~'
                                    elif mark['type'] == 'spoiler':
                                        to_mark = '||' + to_mark + '||'
                                    else:
                                        pass
                                content += to_mark.format(
                                    unmarked_content=str(leaf['text'])
                                )
                    if element['object'] == 'inline':
                        if element['type'] == 'mention':
                            mentioned = element['data']['mention']
                            if mentioned['type'] == 'role':
                                self._raw_role_mentions.append(int(mentioned['id']))
                                content += f'<@{mentioned["id"]}>'
                            elif mentioned['type'] == 'person':
                                content += f'<@{mentioned["id"]}>'

                                self._raw_user_mentions.append(mentioned['id'])
                                if self.server_id:
                                    user = self._state._get_server_member(self.server_id, mentioned['id'])
                                else:
                                    user = self._state._get_user(mentioned['id'])

                                if user:
                                    self._user_mentions.append(user)
                                else:
                                    name = mentioned.get('name')
                                    if mentioned.get('nickname') is True and mentioned.get('matcher') is not None:
                                        name = name.strip('@').strip(name).strip('@')
                                        if not name.strip():
                                            # matcher might be empty, oops - no username is available
                                            name = None
                                    if self.server_id:
                                        self._user_mentions.append(self._state.create_member(
                                            server=self.server,
                                            data={
                                                'id': mentioned.get('id'),
                                                'name': name,
                                                'profilePicture': mentioned.get('avatar'),
                                                'colour': Colour.from_str(mentioned.get('color', '#000')),
                                                'nickname': mentioned.get('name') if mentioned.get('nickname') is True else None,
                                                'type': 'bot' if self.created_by_bot else 'user',
                                            }
                                        ))
                                    else:
                                        self._user_mentions.append(self._state.create_user(data={
                                            'id': mentioned.get('id'),
                                            'name': name,
                                            'profilePicture': mentioned.get('avatar'),
                                            'type': 'bot' if self.created_by_bot else 'user',
                                        }))

                            elif mentioned['type'] in ('everyone', 'here'):
                                # grab the actual display content of the node instead of using a static string
                                try:
                                    content += element['nodes'][0]['leaves'][0]['text']
                                except KeyError:
                                    # give up trying to be fancy and use a static string
                                    content += f'@{mentioned["type"]}'

                                if mentioned['type'] == 'everyone':
                                    self._mentions_everyone = True
                                elif mentioned['type'] == 'here':
                                    self._mentions_here = True

                        elif element['type'] == 'reaction':
                            rtext = element['nodes'][0]['leaves'][0]['text']
                            content += str(rtext)

                        elif element['type'] == 'link':
                            link_text = element['nodes'][0]['leaves'][0]['text']
                            link_href = element['data']['href']
                            if link_href != link_text:
                                content += f'[{link_text}]({link_href})'
                            else:
                                content += link_href

                        elif element['type'] == 'channel':
                            channel = element['data']['channel']
                            if channel.get('id'):
                                self._raw_channel_mentions.append(channel["id"])
                                content += f'<#{channel["id"]}>'
                                channel = self._state._get_server_channel(self.server_id, channel['id'])
                                if channel:
                                    self._channel_mentions.append(channel)

                content += '\n'

            elif node_type == 'markdown-plain-text':
                try:
                    content += node['nodes'][0]['leaves'][0]['text']
                except KeyError:
                    # probably an "inline" non-text node - their leaves are another node deeper
                    content += node['nodes'][0]['nodes'][0]['leaves'][0]['text']

                    if 'reaction' in node['nodes'][0].get('data', {}):
                        emote_id = node['nodes'][0]['data']['reaction']['id']
                        emote = self._state._get_emote(emote_id)
                        if emote:
                            self.emotes.append(emote)

            elif node_type == 'webhookMessage':
                if node['data'].get('embeds'):
                    for msg_embed in node['data']['embeds']:
                        self.embeds.append(Embed.from_dict(msg_embed))

            elif node_type == 'block-quote-container':
                quote_content = []
                for quote_node in node['nodes'][0]['nodes']:
                    if quote_node.get('leaves'):
                        text = str(quote_node['leaves'][0]['text'])
                        quote_content.append(text)

                if quote_content:
                    content += '\n> {}\n'.format('\n> '.join(quote_content))

            elif node_type in {'image', 'video', 'fileUpload'}:
                attachment = Attachment(state=self._state, data=node)
                self.attachments.append(attachment)

        content = content.rstrip('\n')
        # strip ending of newlines in case a paragraph node ended without
        # another paragraph node
        return content