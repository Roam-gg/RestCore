from typing import Dict, Union, Optional, Any
from functools import partial
import abc
import asyncio

class Service(abc.ABC):
    _AUTH_SERVICE = False
    @abc.abstractmethod
    def __init__(self, *args, extensions: Dict[str, 'Extension'], **kwargs):
        pass

    @classmethod
    def service_factory(cls, *args, **kwargs):
        return partial(cls, *args, **kwargs)

class AuthService(Service):
    _AUTH_SERVICE = True

    @abc.abstractmethod
    def __call__(self, auth_str: str) -> bool:
        pass

    @abc.abstractmethod
    def get_user(self, auth_str: str) -> Optional[Any]:
        pass
