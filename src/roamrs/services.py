from typing import Dict
from functools import partial
import abc
import asyncio

class Service(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, extensions: Dict[str, 'Extension'], **kwargs):
        pass

    @classmethod
    def service_factory(cls, *args, **kwargs):
        return partial(cls, *args, **kwargs)
