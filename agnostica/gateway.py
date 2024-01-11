"""This file contains code from guilded.py and discord.py, see LICENSE.txt for full license details."""
from __future__ import annotations
import datetime
import re

import time
import aiohttp
import asyncio
import concurrent.futures
import json
import logging
import sys
import threading
import traceback

from typing import TYPE_CHECKING, Dict, Optional, Any

from .adapters import PlatformAdapter
from .globals import platform
from .errors import AgnosticaException, HTTPException

if TYPE_CHECKING:
    from typing_extensions import Self

log = logging.getLogger(__name__)

class WebSocketClosure(Exception):
    """An exception to make up for the fact that aiohttp doesn't signal closure"""
    def __init__(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.data: Optional[Dict[str, Any]]
        try:
            self.data = json.loads(message)
        except:
            self.data = None
        
        super().__init__(message)

class WebSocket:
    """Implements a base WebSocket for adapters to use."""
    def __init__(self, socket: aiohttp.ClientWebSocketResponse, *, loop: asyncio.AbstractEventLoop, _platform: PlatformAdapter):
        self._platform = _platform or platform
        self.loop = loop
        self._heartbeater = None

        self.socket: aiohttp.ClientWebSocketResponse = socket
        self._close_code: Optional[int] = None
    
    @property
    def latency(self) -> float:
        return self._heartbeater.latency if self._heartbeater else float('inf')
    
    @classmethod
    async def connect(cls, platform: PlatformAdapter, *, loop: asyncio.AbstractEventLoop = None) -> Self:
        try:
            socket = await platform.ws_connect()
        except aiohttp.WSServerHandshakeError as e:
            log.error(f"Failed to connect to websocket: {e}")
            return e
        else:
            log.info(f"Connected to websocket.")
        
        ws = cls(socket, _platform=platform, loop=loop or asyncio.get_event_loop())
        await ws.ping()

        return ws

class Heartbeater(threading.Thread):
    def __init__(self, ws: WebSocket, interval: float):
        self.ws = ws
        self.interval = interval
        super().__init__()

        self.msg = "Keeping websocket alive with sequence %s."
        self.block_msg = "Websocket heartbeat blocked for longer than %s seconds."
        self.behind_msg = "Can't keep up, websocket is %.1fs behind."
        self._stop_ev = threading.Event()

        self._last_ping: float = time.perf_counter()
        self._last_pong: float = time.perf_counter()
        self.latency: float = float('inf')
    
    def run(self):
        log.debug("Starting heartbeat thread.")
        while not self._stop_ev.wait(self.interval):
            log.debug("Sending heartbeat.")
            coro = self.ws.ping()
            f = asyncio.run_coroutine_threadsafe(coro, self.ws.loop)
            try:
                total = 0
                while True:
                    try:
                        f.result(10)
                        break
                    except concurrent.futures.TimeoutError:
                        total += 10
                        try:
                            frame = sys._current_frames()[self._main_thread_id]
                        except KeyError:
                            msg = self.block_msg
                        else:
                            stack = traceback.format_stack(frame)
                            msg = '%s\nLoop thread traceback (most recent call last):\n%s' % (self.block_msg, ''.join(stack))
                        log.warning(msg, total)
            except Exception:
                self.stop()
            else:
                self._last_ping = time.perf_counter()
        
    def stop(self) -> None:
        self._stop_ev.set()
    
    def record_pong(self) -> None:
        self._last_pong = time.perf_counter()
        self.latency = self._last_pong - self._last_ping

        if self.latency > 10:
            log.warning(self.behind_msg, self.latency)