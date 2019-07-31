from typing import Dict

import abc
import asyncio


class Extension(abc.ABC):
    def __init__(self):
        self.services = None

    @abc.abstractmethod
    async def __call__(self, services):
        pass

    @abc.abstractmethod
    async def stop(self):
        pass

class ExampleExtension(Extension):
    def __init__(self, counter):
        super().__init__(services)
        self.counter = counter
        self.stop_event = asyncio.Event()

    async def __call__(self, services):
        self.services = services
        while self.counter >= 0 and not self.stop_event.is_set():
            await asyncio.sleep(1)
            self.counter -= 1
        print('done!')

    async def stop(self):
        self.stop_event.set()
