"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from typing import Any, Dict, Optional, overload

from agnostica.globals import _cv_platform
from agnostica.http import HTTPClientBase
from agnostica.embed import Embed
from agnostica.colour import Colour
from agnostica.channel import DMChannel
from agnostica.server import Server

import agnostica.abc
import datetime

def unimplementedFunction():
    raise NotImplementedError("This function is not implemented yet by the adapter. If this is a mistake please report this to the adapter's maintainer.")

class PlatformAdapter:
    """A base adapter class for interactions with a bot on a platform."""
    _supported_auth_methods = ["token", "credentials"]
    _http_client = HTTPClientBase

    ATTACHMENT_REGEX = ""

    BASE = ""
    PROFILE_BASE: Optional[str] = None
    VANITY_BASE: Optional[str] = None
    DEFAULT_DATE: Optional[datetime.datetime] = None

    def __enter__(self):
        self._cv_token = _cv_platform.set(self)
    
    def __exit__(self, exc_type, exc_value, traceback):
        _cv_platform.reset(self._cv_token)
        self._cv_token = None
    
    def __setup__(self, name: str, *args, **kwargs):
        self.http = self._http_client(*args, **kwargs)
        if name:
            self.name = name
        else:
            self.name = self.__class__.__name__.removesuffix("Adapter")

    @overload
    def __init__(self, token: str, name: str=None, *args, **kwargs):
        if not 'token' in self._supported_auth_methods:
            raise ValueError(f"Token-based authentication is not supported by {self.__class__.__name__}")
        self.authentication = {
            "type": "token",
            "token": token,
        }
        self.__setup__(name=name, *args, **kwargs)
    
    @overload
    def __init__(self, username: str, password: str, name: str=None, *args, **kwargs):
        if not 'credentials' in self._supported_auth_methods:
            raise ValueError(f"Credential-based authentication is not supported by {self.__class__.__name__}")
        self.authentication = {
            "type": "credentials",
            "username": username,
            "password": password,
        }
        self.__setup__(name=name, *args, **kwargs)
    
    @property
    def type(self) -> str:
        return self.__class__.__name__.removesuffix("Adapter").lower()
    
    def get_channel_share_url(self, channel: agnostica.abc.ServerChannel) -> str:
        return self.BASE
    
    def get_user_profile_url(self, user: agnostica.abc.User) -> str:
        return f'{self.PROFILE_BASE}/{user.id}'
    
    def get_user_vanity_url(self, user: agnostica.abc.User) -> str:
        return f'{self.VANITY_BASE}/{user.slug}'
    
    def get_dm_channel_share_url(self, channel: DMChannel) -> str:
        return self.BASE
    
    def get_server_vanity_url(self, server: Server) -> Optional[str]:
        return f'https://guilded.gg/{server.slug}' if server.slug else None
    
    async def get_channel(self, server_id: str, channel_id: str):
        unimplementedFunction()
    
    def get_full_content(self, data: Dict[str, Any]):
        raise NotImplementedError('Received none-string content data from adapter but adapter has not implemented _get_full_content!')
    
    def embed_to_dict(self, embed: Embed):
        """Converts an embed to a format the target platform can work with.
        
        By default this will convert to a Discord/Guilded compatible format."""
        # add in the raw data into the dict
        result = {
            key[1:]: getattr(embed, key)
            for key in embed.__slots__
            if key[0] == '_' and hasattr(embed, key)
        }

        # deal with basic convenience wrappers

        try:
            colour: Colour = result.pop('colour')
        except KeyError:
            pass
        else:
            if colour:
                result['color'] = colour.value

        try:
            timestamp = result.pop('timestamp')
        except KeyError:
            pass
        else:
            if timestamp:
                if timestamp.tzinfo:
                    result['timestamp'] = timestamp.astimezone(tz=datetime.timezone.utc).isoformat()
                else:
                    result['timestamp'] = timestamp.replace(tzinfo=datetime.timezone.utc).isoformat()

        # add in the non raw attribute ones
        if embed.type:
            result['type'] = embed.type

        if embed.description:
            result['description'] = embed.description

        if embed.url:
            result['url'] = embed.url

        if embed.title:
            result['title'] = embed.title
        
        return result