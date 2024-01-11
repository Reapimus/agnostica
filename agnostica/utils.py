"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from typing import Any, AsyncIterable, Callable, Coroutine, Iterable, TypeVar, Union
from operator import attrgetter

from .mixins import Hashable
from .globals import platform

valid_image_extensions = ['png', 'webp', 'jpg', 'jpeg', 'gif', 'jif', 'tif', 'tiff', 'apng', 'bmp', 'svg']
valid_video_extensions = ['mp4', 'mpeg', 'mpg', 'mov', 'avi', 'wmv', 'qt', 'webm']

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
_Iter = Union[Iterable[T], AsyncIterable[T]]
Coro = Coroutine[Any, Any, T]

class _MissingSentinel:
    def __eq__(self, _) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return '...'

MISSING: Any = _MissingSentinel()

def get(sequence, **attributes):
    """Return an object from ``sequence`` that matches the ``attributes``.

    If nothing is found, ``None`` is returned.

    Parameters
    -----------
    sequence
        An iterable to search through.
    **attrs
        Keyword arguments representing attributes of each item to match with.
    """
    # global -> local
    _all = all
    attrget = attrgetter

    # Special case the single element call
    if len(attributes) == 1:
        k, v = attributes.popitem()
        pred = attrget(k.replace('__', '.'))
        for elem in sequence:
            if pred(elem) == v:
                return elem
        return None

    converted = [
        (attrget(attr.replace('__', '.')), value)
        for attr, value in attributes.items()
    ]

    for elem in sequence:
        if _all(pred(elem) == value for pred, value in converted):
            return elem
    return None

def copy_doc(original: Callable) -> Callable[[T], T]:
    def decorator(overridden: T) -> T:
        overridden.__doc__ = original.__doc__
        overridden.__signature__ = _signature(original)  # type: ignore
        return overridden

    return decorator

class Object(Hashable):
    """Represents a generic platform object.
    
    This class is especially useful when interfacing with platforms
    where often only an object's ID is available.
    
    Attributes
    -----------
    id: Union[:class:`str`, :class:`int`]
        The ID of the object.
    """

    def __init__(self, id: Union[str, int]):
        if not isinstance(id, (str, int)):
            raise TypeError(f'id must be type str or int, not {id.__class__.__name__}')

        if isinstance(id, str) and id == '@me':
            id = platform.user.id
        
        self.id: Union[str, int] = id
    
    def __repr__(self) -> str:
        return f'<Object id={self.id!r}>'