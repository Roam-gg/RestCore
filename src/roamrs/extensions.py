from __future__ import annotations

from typing import Dict
from .services import Service
import abc
import asyncio


class Extension(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def __call__(self, services: Dict[str, Service], extensions: Dict[str, Extension]):
        pass

    @abc.abstractmethod
    async def stop(self):
        pass

class ExampleExtension(Extension):
    def __init__(self, counter):
        super().__init__()
        self.counter = counter
        self.stop_event = asyncio.Event()
        self.services = None
        self.extensions = None

    async def __call__(self, services, extensions):
        self.services = services
        self.extensions = extensions
        while self.counter >= 0 and not self.stop_event.is_set():
            await asyncio.sleep(1)
            self.counter -= 1
        print('done!')

    async def stop(self):
        self.stop_event.set()
