"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
import io
import os
import re
from typing import Any, Dict, Optional, Union

from .asset import AssetMixin
from .globals import platform
from . import utils


__all__ = (
    'Attachment',
    'File',
)


class File:
    """Wraps files pre- and mid-upload.

    .. container:: operations

        .. describe:: bytes(x)

            Returns the bytes of the underlying file.

    Parameters
    -----------
    fp: Union[:class:`os.PathLike`, :class:`io.BufferedIOBase`]
        The file to upload.
        If passing a file with ``open``, the file should be opened in ``rb`` mode.
    filename: Optional[:class:`str`]
        The name of this file.
    file_type: :class:`FileType`
        The file's file type.
        If this could not be detected by the library, defaults to :attr:`FileType.image`. 

    Attributes
    -----------
    fp: Union[:class:`os.PathLike`, :class:`io.BufferedIOBase`]
        The file ready to be uploaded to the platform.
    filename: Optional[:class:`str`]
        The name of the file.
    file_type: :class:`FileType`
        The file's file type.
    url: Optional[:class:`str`]
        The URL to the file on the platform's CDN after being uploaded by the library.
    """

    __slots__ = (
        '_state',
        'fp',
        'filename',
        'type',
        'file_type',
        'url',
        '_owner',
        '_original_pos',
        '_closer',
    )

    def __init__(
        self,
        fp: Union[str, bytes, io.BufferedIOBase],
        *,
        filename: Optional[str] = None,
    ):
        self.url: Optional[str] = None
        self.filename: Optional[str] = filename

        if isinstance(fp, io.IOBase):
            if not (fp.seekable() and fp.readable()):
                raise ValueError(f'File buffer {fp!r} must be seekable and readable')

            self.fp: io.BufferedIOBase = fp
            self._owner = False
            self._original_pos = fp.tell()

            self.fp.name = getattr(self.fp, 'name', self.filename)

        else:
            self.fp = open(fp, 'rb')
            self._owner = True
            self._original_pos = 0

        self._closer = self.fp.close
        self.fp.close = lambda: None

    def __repr__(self) -> str:
        return f'<File type={self.type}>'

    def __bytes__(self) -> bytes:
        return self.fp.read()

    def reset(self, *, seek: Union[int, bool] = True) -> None:
        # https://github.com/Rapptz/discord.py/blob/5c14149873368060c0b86c95914753ab7b283097/discord/file.py#L134-L141
        if seek:
            self.fp.seek(self._original_pos)

    def close(self) -> None:
        self.fp.close = self._closer
        if self._owner:
            self._closer()

    async def _upload(self):
        data = await platform.upload_file(self)
        url = data.get('url')
        self.url = url
        return self


class Attachment(AssetMixin):
    """An uploaded attachment in a message, announcement, document, or any
    other place you can upload files inline with content.

    Attributes
    -----------
    url: :class:`str`
        The URL to the file on the platform's CDN.
    file_type: Optional[:class:`FileType`]
        The type of file.
    caption: Optional[:class:`str`]
        The attachment's caption.
    size: Optional[:class:`int`]
        The attachment's size in bytes.
    height: Optional[:class:`int`]
        The attachment's height in pixels.
    width: Optional[:class:`int`]
        The attachment's width in pixels.
    """

    __slots__ = (
        '_state',
        'url',
        'width',
        'height',
        'size',
        'filename',
    )

    def __init__(self, *, state, data: Dict[str, Any], **extra):
        self._state = state

        self.size: Optional[int] = data.get('size')
        self.filename: Optional[str] = data.get('name')

        self.url: str = data.get('url')
        self.width: Optional[int] = data.get('width')
        self.height: Optional[int] = data.get('height')
        self.content_type: Optional[str] = data.get('content_type')
        self.description: Optional[str] = data.get('description')

    def __repr__(self) -> str:
        return f'<Attachment filename={self.filename!r} url={self.url!r}>'

    def __str__(self) -> str:
        return self.url

    async def to_file(self) -> File:
        """|coro|

        Converts the attachment to an uploadable :class:`File` instance.

        Returns
        --------
        :class:`File`
            The attachment as a :class:`File`.
        """

        data = io.BytesIO(await self.read())
        file = File(data, filename=self.filename)
        return file