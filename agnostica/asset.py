"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
import io
import os
from typing import Any, Optional, Tuple, Union
from urllib.parse import quote_plus
import yarl

from .errors import AgnosticaException, InvalidArgument

__all__ = (
    'Asset',
)

class AssetMixin:
    url: str
    _state: Optional[Any]

    async def read(self) -> bytes:
        """|coro|

        Retrieves the content of this asset as a :class:`bytes` object.

        Raises
        -------
        AgnosticaException
            There was no internal connection state.
        HTTPException
            Downloading the asset failed.
        NotFound
            The asset was deleted.

        Returns
        --------
        :class:`bytes`
            The content of the asset.
        """
        if self._state is None:
            raise AgnosticaException('Invalid state (none provided)')

        return await self._state.read_filelike_data(self)

    async def save(self, fp: Union[str, bytes, os.PathLike, io.BufferedIOBase], *, seek_begin: bool = True) -> int:
        """|coro|

        Saves this asset into a file-like object.

        Parameters
        -----------
        fp: Union[:class:`io.BufferedIOBase`, :class:`os.PathLike`]
            The file-like object to save this attachment to or the filename
            to use. If a filename is passed then a file is created with that
            filename and used instead.
        seek_begin: :class:`bool`
            Whether to seek to the beginning of the file after saving is
            successfully done.

        Raises
        -------
        AgnosticaException
            There was no internal connection state.
        HTTPException
            Downloading the asset failed.
        NotFound
            The asset was deleted.

        Returns
        --------
        :class:`int`
            The number of bytes written.
        """

        data = await self.read()
        if isinstance(fp, io.BufferedIOBase):
            written = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return written
        else:
            with open(fp, 'wb') as f:
                return f.write(data)

    async def bytesio(self):
        """|coro|

        Fetches the raw data of this asset and wraps it in a
        :class:`io.BytesIO` object.

        Raises
        -------
        AgnosticaException
            There was no internal connection state.
        HTTPException
            Downloading the asset failed.
        NotFound
            The asset was deleted.

        Returns
        --------
        :class:`io.BytesIO`
            The asset as a ``BytesIO`` object.
        """
        data = await self.read()
        return io.BytesIO(data)

class Asset(AssetMixin):
    """Represents an asset on a platform.

    .. container:: operations

        .. describe:: x == y

            Checks if two assets are equal (have the same URL).

        .. describe:: x != y

            Checks if two assets are not equal.

        .. describe:: str(x)

            Returns the URL of the asset.

        .. describe:: len(x)

            Returns the length of the asset's URL.

        .. describe:: bool(x)

            Returns ``True`` if the asset has a URL.
    """

    __slots__: Tuple[str, ...] = (
        '_state',
        '_url',
        '_animated',
        '_key',
    )

    BASE = ''

    VALID_STATIC_FORMATS = frozenset({'jpeg', 'jpg', 'webp', 'png'})
    VALID_ASSET_FORMATS = VALID_STATIC_FORMATS | {'gif', 'apng'}

    def __init__(
        self,
        state,
        *,
        url: str,
        key: str,
        animated: bool = False,
        maybe_animated: bool = False,
        banner: bool = False,
    ):
        self._state = state
        self._url = url

        # Force unity if we know a value of one that should affect the other
        if animated:
            maybe_animated = True
        if not maybe_animated:
            animated = False

        self._animated = animated
        self._maybe_animated = maybe_animated
        self._key = key
        self._banner = banner

    def __str__(self) -> str:
        return self._url

    def __len__(self) -> int:
        return len(self._url)

    def __repr__(self):
        shorten = self._url.replace(self.BASE, '')
        return f'<Asset url={shorten!r}>'

    def __eq__(self, other):
        return isinstance(other, Asset) and self._url == other._url

    def __hash__(self):
        return hash(self._url)

    @property
    def url(self) -> str:
        """:class:`str`: The underlying URL of the asset."""
        return self._url

    @property
    def key(self) -> str:
        """:class:`str`: The identifying key of the asset."""
        return self._key

    @property
    def aws_url(self) -> str:
        """:class:`str`: The underlying URL of the asset on AWS. for platforms that
        support it this will return the AWS url, for those that don't this will
        return the CDN url."""
        return self._url

    def strip_cdn_url(self, url: str) -> str:
        """Returns the identifying key from an entire CDN URL. This exists because
        the API returns full URLs instead of only hashes/names, but we want to be
        able to modify size and format freely."""
        raise NotImplementedError
    
    def convert_size(self, size: Union(str, int), *, banner: bool = False) -> Union(str, int):
        """Converts the specified size to something that the platform this asset is for
        supports."""
        raise NotImplementedError

    def is_animated(self) -> bool:
        """:class:`bool`: Returns whether the asset is animated.

        .. note::

            This may return false negatives for assets like user or bot
            avatars which have no definitive indicator.
        """
        return self._animated

    def replace(
        self,
        *,
        size: str = None,
        format: str = None,
        static_format: str = None,
    ):
        """Returns a new asset with the passed components replaced.

        .. warning::

            If this asset is a user or bot avatar, you should not replace
            ``format`` because avatars uploaded after 10 May 2022 can only
            use the ``webp`` format.

        Parameters
        -----------
        size: :class:`str`
            The new size of the asset. Must be one of
            'Small', 'Medium', 'Large', or 'HeroMd' or 'Hero' if it's a banner.
        format: :class:`str`
            The new format to change it to. Must be one of
            'webp', 'jpeg', 'jpg', 'png', or 'gif' or 'apng' if it's animated.
        static_format: :class:`str`
            The new format to change it to if the asset isn't animated.
            Must be either 'webp', 'jpeg', 'jpg', or 'png'.

        Raises
        -------
        InvalidArgument
            An invalid size or format was passed.

        Returns
        --------
        :class:`.Asset`
            The newly updated asset.
        """
        url = yarl.URL(self._url)
        path, extension = os.path.splitext(url.path)
        extension = extension.lstrip('.')
        current_size = url.path.split('-')[1].replace(f'.{extension}', '')

        if format is not None:
            if self._maybe_animated:
                if format not in self.VALID_ASSET_FORMATS:
                    raise InvalidArgument(f'format must be one of {self.VALID_ASSET_FORMATS}')
            else:
                if format not in self.VALID_STATIC_FORMATS:
                    raise InvalidArgument(f'format must be one of {self.VALID_STATIC_FORMATS}')
            url = url.with_path(f'{path}.{format}')
            extension = format

        if static_format is not None and not self._maybe_animated:
            if static_format not in self.VALID_STATIC_FORMATS:
                raise InvalidArgument(f'static_format must be one of {self.VALID_STATIC_FORMATS}')
            url = url.with_path(f'{path}.{static_format}')
            extension = static_format

        if size is not None:
            size = self.convert_size(size, banner=self._banner)
            url = url.with_path(f'{path.replace(current_size, size)}.{extension}')

        url = str(url)
        return Asset(state=self._state, url=url, key=self._key, animated=self._animated, maybe_animated=self._maybe_animated, banner=self._banner)

    def with_size(self, size: str):
        """Returns a new asset with the specified size.

        Parameters
        -----------
        size: :class:`str`
            The new size of the asset.

        Raises
        -------
        InvalidArgument
            The asset had an invalid size.

        Returns
        --------
        :class:`.Asset`
            The newly updated asset.
        """
        size = self.convert_size(size, banner=self._banner)
        url = yarl.URL(self._url)
        path, extension = os.path.splitext(url.path)
        extension = extension.lstrip('.')
        current_size = url.path.split('-')[1].replace(f'.{extension}', '')
        url = str(url.with_path(f'{path.replace(current_size, size)}.{extension}'))
        return Asset(state=self._state, url=url, key=self._key, animated=self._animated, maybe_animated=self._maybe_animated)

    def with_format(self, format: str):
        """Returns a new asset with the specified format.

        .. warning::

            If this asset is a user or bot avatar, you should not use this
            method because avatars uploaded after 10 May 2022 can only use the
            ``webp`` format.

        Parameters
        -----------
        format: :class:`str`
            The new format of the asset.

        Raises
        -------
        InvalidArgument
            The asset had an invalid format.

        Returns
        --------
        :class:`.Asset`
            The newly updated asset.
        """

        if self._maybe_animated:
            if format not in self.VALID_ASSET_FORMATS:
                raise InvalidArgument(f'format must be one of {self.VALID_ASSET_FORMATS}')
        else:
            if format not in self.VALID_STATIC_FORMATS:
                raise InvalidArgument(f'format must be one of {self.VALID_STATIC_FORMATS}')

        url = yarl.URL(self._url)
        path, _ = os.path.splitext(url.path)
        url = str(url.with_path(f'{path}.{format}'))
        return Asset(state=self._state, url=url, key=self._key, animated=self._animated, maybe_animated=self._maybe_animated)

    def with_static_format(self, format: str):
        """Returns a new asset with the specified static format.

        This only changes the format if the underlying asset is
        not animated. Otherwise, the asset is not changed.

        Parameters
        -----------
        format: :class:`str`
            The new static format of the asset.

        Raises
        -------
        InvalidArgument
            The asset had an invalid format.

        Returns
        --------
        :class:`.Asset`
            The newly updated asset.
        """

        if self._maybe_animated:
            return self
        return self.with_format(format)