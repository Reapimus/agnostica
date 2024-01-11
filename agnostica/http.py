"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Union, NamedTuple, List, Sequence, TypeVar, Type

import aiohttp
import asyncio
import logging
import json

from .file import File, Attachment
from .asset import Asset
from .gateway import WebSocket
from .utils import MISSING
from .embed import Embed

from . import __version__
from .errors import Forbidden, PlatformServerError, HTTPException, NotFound
import sys

if TYPE_CHECKING:
    from typing_extensions import Self
    from types import TracebackType

    from .types.channel import ServerChannel as ServerChannelPayload

    from .asset import Asset
    from .category import Category
    from .channel import DMChannel, Thread
    from .emote import Emote
    from .file import Attachment, File
    from .gateway import WebSocket
    from .role import Role
    from .server import Server
    from .user import ClientUser

    T = TypeVar('T')
    BE = TypeVar('BE', bound=BaseException)

log = logging.getLogger(__name__)

class MultipartParameters(NamedTuple):
    payload: Optional[Dict[str, Any]]
    multipart: Optional[List[Dict[str, Any]]]
    files: Optional[Sequence[File]]

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BE]],
        exc: Optional[BE],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.files:
            for file in self.files:
                file.close()


def handle_message_parameters(
    content: Optional[str] = MISSING,
    *,
    username: str = MISSING,
    avatar_url: Any = MISSING,
    file: File = MISSING,
    files: Sequence[File] = MISSING,
    embed: Optional[Embed] = MISSING,
    embeds: Sequence[Embed] = MISSING,
    reply_to: Sequence[str] = MISSING,
    silent: Optional[bool] = None,
    private: Optional[bool] = None,
    hide_preview_urls: Sequence[str] = MISSING,
) -> MultipartParameters:
    if files is not MISSING and file is not MISSING:
        raise TypeError('Cannot mix file and files keyword arguments.')
    if embeds is not MISSING and embed is not MISSING:
        raise TypeError('Cannot mix embed and embeds keyword arguments.')

    if file is not MISSING:
        files = [file]

    payload = {}
    if embeds is not MISSING:
        if len(embeds) > 10:
            raise ValueError('embeds has a maximum of 10 elements.')
        payload['embeds'] = [e.to_dict() for e in embeds]

    if embed is not MISSING:
        if embed is None:
            payload['embeds'] = []
        else:
            payload['embeds'] = [embed.to_dict()]

    if content is not MISSING:
        if content is not None:
            payload['content'] = str(content)
        else:
            payload['content'] = None

    if reply_to is not MISSING:
        payload['replyMessageIds'] = reply_to

    if silent is not None:
        payload['isSilent'] = silent

    if private is not None:
        payload['isPrivate'] = private

    if hide_preview_urls is not MISSING:
        payload['hiddenLinkPreviewUrls'] = hide_preview_urls

    if username:
        payload['username'] = username

    if avatar_url:
        payload['avatar_url'] = str(avatar_url)

    multipart = []
    if files:
        multipart.append({'name': 'payload_json', 'value': json.dumps(payload)})
        payload = None
        for index, file in enumerate(files):
            multipart.append({
                'name': f'files[{index}]',
                'value': file.fp,
                'filename': file.filename,
            })

    return MultipartParameters(payload=payload, multipart=multipart, files=files)

async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding='utf-8')
    try:
        if response.headers['content-type'] == 'application/json':
            return json.loads(text)
    except KeyError:
        pass
    
    return text

class Route:
    BASE = ''

    def __init__(self, method: str, path: str, *, override_base: Optional[str]=None):
        self.method = method
        self.path = path
        
        if override_base is not None:
            self.BASE = override_base

        self.url = self.BASE + self.path

class HTTPClientBase:
    BASE = ''
    NO_BASE = ''

    def __init__(self, *, max_messages: Optional[int]=1000):
        self.session: Optional[aiohttp.ClientSession] = None
        self.max_messages = max_messages

        self.ws: Optional[WebSocket] = None
        # self.user: Optional[ClientUser] = None
        self.my_id: Optional[str] = None

        self._users = {}
        self._servers = {}
        self._emojis = {}
        self._dm_channels = {}
        self._messages = {}

        self.token: Optional[str] = None

        user_agent = 'agnostica/{0} (https://github.com/Reapimus/agnostica) Python{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)
    
    async def request(self, route: Route, **kwargs):
        url = route.url
        method = route.method

        headers: Dict[str, str] = {
            'User-Agent': self.user_agent,
        }

        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs.pop('json'))
        
        kwargs['headers'] = headers

        log_url = url
        if kwargs.get('params'):
            if isinstance(kwargs['params'], dict):
                log_url = url + '?' + '&'.join(f'{k}={v}' for k, v in kwargs['params'].items())
            elif isinstance(kwargs['params'], Iterable):
                log_url = url + '?' + '&'.join(kwargs['params'])
        
        log_headers = headers.copy()
        if 'Authorization' in log_headers:
            log_headers['Authorization'] = 'Bearer [removed]'
        
        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None
        for tries in range(5):
            try:
                response = await self.session.request(method, url, **kwargs)
            except OSError as exc:
                if tries < 4 and exc.errno in (54, 10054):
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise
        
            log.debug('%s %s with data %s, headers %s has returned %s', method, log_url, kwargs.get('data'), log_headers, response.status)

            if response.headers.get('Content-Type', '').startswith(('image/', 'video/')):
                data = await response.read()
            else:
                data = await json_or_text(response)
                log.debug('%s %s has received %s', method, log_url, data)
            
            # The request was successful so just return the response
            if 300 > response.status >= 200:
                return data
            
            if response.status == 429:
                retry_after = response.headers.get('retry-after')
                retry_after = float(retry_after) if retry_after is not None else (1 + tries * 2)

                log.warning(
                    'Rate limited on %s. Retrying in %s seconds',
                    route.path,
                    retry_after,
                )
                await asyncio.sleep(retry_after)
                log.debug('Done sleeping for the rate limit. Retrying...')

                continue
            
            # We've received a 500, 502, 504, or 524, unconditional retry
            if response.status in {500, 502, 504, 524}:
                await asyncio.sleep(1 + tries * 2)
                continue
            
            if response.status == 403:
                raise Forbidden(response, data)
            elif response.status == 404:
                raise NotFound(response, data)
            elif response.status >= 500:
                raise PlatformServerError(response, data)
            else:
                raise HTTPException(response, data)
        
        if response is not None:
            # We've run out of retries
            if response.status >= 500:
                raise PlatformServerError(response, data)

            raise HTTPException(response, data)

        raise RuntimeError('Unreachable code in HTTP handling')
    
    async def close(self) -> None:
        if self.session:
            await self.session.close()
    
    @property
    def _all_server_channels(self) -> Dict[str, Any]:
        all_channels = {}
        for server in self._servers.values():
            all_channels.update(server._channels)
    
    def read_filelike_data(self, filelike: Union[Attachment, Asset, File]):
        return self.request(Route('GET', filelike.url, override_base=self.NO_BASE))