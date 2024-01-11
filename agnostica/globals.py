from __future__ import annotations

from agnostica.adapters.base import PlatformAdapter
from contextvars import ContextVar

_cv_platform: ContextVar[PlatformAdapter] = ContextVar("agnostica.platform")
platform: PlatformAdapter = _cv_platform.get()