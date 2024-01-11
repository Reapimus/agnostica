"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
import re

from urllib.parse import quote_plus
from typing import Optional, Union
from agnostica import Asset, InvalidArgument

__all__ = (
    'GuildedAsset',
)

def convert_int_size(size: int, *, banner: bool = False) -> Optional[str]:
    """Converts an integer passed to Asset.with_size or Asset.replace to a
    Guilded-compliant size for discord.py compatibility."""
    if not size & (size - 1) and 4096 >= size >= 16:
        if size >= 1024:
            return 'Hero' if banner else 'Large'
        elif 1024 > size >= 512:
            return 'HeroMd' if banner else 'Medium'
        elif 0 <= size < 512:
            return 'HeroMd' if banner else 'Small'

class GuildedAsset(Asset):
    VALID_BANNER_SIZES = frozenset({'HeroMd', 'Hero'})
    VALID_ASSET_SIZES = {'Small', 'Medium', 'Large'} | VALID_BANNER_SIZES

    BASE = 'https://img.guildedcdn.com'
    GIL_BASE = 'https://cdn.gilcdn.com'
    AWS_BASE = 'https://s3-us-west-2.amazonaws.com/www.guilded.gg'

    def strip_cdn_url(self, url: str) -> str:
        match = re.search(r'\/(?P<key>[a-zA-Z0-9]+)-(?P<size>\w+)\.(?P<format>[a-z]+)', url)
        if match:
            return match.group('key')
        raise ValueError(f'Invalid CDN URL: {url}')
    
    def convert_size(self, size: Union(str, int), *, banner: bool = False) -> Union(str, int):
        if isinstance(size, int):
            size = convert_int_size(size, banner=self._banner)
            if self._banner:
                if size not in self.VALID_BANNER_SIZES:
                    raise InvalidArgument(f'size must be one of {self.VALID_BANNER_SIZES} or be a power of 2 between 16 and 4096')
            else:
                if size not in self.VALID_ASSET_SIZES:
                    raise InvalidArgument(f'size must be one of {self.VALID_ASSET_SIZES} or be a power of 2 between 16 and 4096')
        return size
    
    @classmethod
    def _from_default_user_avatar(cls, state, number: int):
        key = f'profile_{number}'
        return cls(
            state,
            url=f'{cls.BASE}/asset/DefaultUserAvatars/{key}.png',
            key=key,
        )

    @classmethod
    def _from_user_avatar(cls, state, image_url: str):
        animated = 'ia=1' in image_url
        maybe_animated = '.webp' in image_url
        format = 'webp' if animated or maybe_animated else 'png'
        image_hash = cls.strip_cdn_url(image_url)
        return cls(
            state,
            url=f'{cls.BASE}/UserAvatar/{image_hash}-Large.{format}',
            key=image_hash,
            animated=animated,
            maybe_animated=maybe_animated,
        )

    @classmethod
    def _from_user_banner(cls, state, image_url: str):
        image_hash = cls.strip_cdn_url(image_url)
        return cls(
            state,
            url=f'{cls.BASE}/UserBanner/{image_hash}-Hero.png',
            key=image_hash,
            banner=True,
        )

    @classmethod
    def _from_team_avatar(cls, state, image_url: str):
        image_hash = cls.strip_cdn_url(image_url)
        return cls(
            state,
            url=f'{cls.BASE}/TeamAvatar/{image_hash}-Large.png',
            key=image_hash,
        )

    @classmethod
    def _from_team_banner(cls, state, image_url: str):
        image_hash = cls.strip_cdn_url(image_url)
        return cls(
            state,
            url=f'{cls.BASE}/TeamBanner/{image_hash}-Hero.png',
            key=image_hash,
            banner=True,
        )

    @classmethod
    def _from_group_avatar(cls, state, image_url: str):
        image_hash = cls.strip_cdn_url(image_url)
        return cls(
            state,
            url=f'{cls.BASE}/GroupAvatar/{image_hash}-Large.png',
            key=image_hash,
        )

    @classmethod
    def _from_group_banner(cls, state, image_url: str):
        image_hash = cls.strip_cdn_url(image_url)
        return cls(
            state,
            url=f'{cls.BASE}/GroupBanner/{image_hash}-Large.png',
            key=image_hash,
        )

    @classmethod
    def _from_custom_reaction(cls, state, image_url: str, animated: bool = False):
        image_hash = cls.strip_cdn_url(image_url)
        format = 'apng' if animated else 'webp'
        return cls(
            state,
            url=f'{cls.BASE}/CustomReaction/{image_hash}-Full.{format}',
            key=image_hash,
            animated=animated,
        )

    @classmethod
    def _from_guilded_stock_reaction(cls, state, name: str, animated: bool = False):
        format = 'apng' if animated else 'webp'
        name = quote_plus(name)
        return cls(
            state,
            url=f'{cls.BASE}/asset/Emojis/Custom/{name}.{format}',
            key=name,
            animated=animated,
        )

    @classmethod
    def _from_unicode_stock_reaction(cls, state, name: str, animated: bool = False):
        format = 'apng' if animated else 'webp'
        name = quote_plus(name)
        return cls(
            state,
            url=f'{cls.BASE}/asset/Emojis/{name}.{format}',
            key=name,
            animated=animated,
        )

    @classmethod
    def _from_default_bot_avatar(cls, state, url: str):
        name = cls.strip_cdn_url(url)
        return cls(
            state,
            url=f'{cls.BASE}/asset/DefaultBotAvatars/{name}.png',
            key=name,
        )

    @classmethod
    def _from_webhook_thumbnail(cls, state, image_url: str):
        animated = 'ia=1' in image_url
        image_hash = cls.strip_cdn_url(image_url)
        return cls(
            state,
            url=f'{cls.BASE}/WebhookThumbnail/{image_hash}-Full.webp',
            key=image_hash,
            animated=animated,
            maybe_animated=True,
        )

    @classmethod
    def _from_media_thumbnail(cls, state, url: str):
        image_hash = cls.strip_cdn_url(url)
        return cls(
            state,
            url=url,
            key=image_hash,
        )
        # We use the original URL here because in testing I could not find an example
        # of a media thumbnail. It may be an old property that is no longer ever populated

    @classmethod
    def _from_default_asset(cls, state, name: str):
        name = quote_plus(name)
        return cls(
            state,
            url=f'{cls.BASE}/asset/Default/{name}-lg.png',
            key=name,
        )