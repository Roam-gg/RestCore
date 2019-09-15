from __future__ import annotations

from dataclasses import dataclass
from typing import Coroutine
from inspect import iscoroutinefunction

from aiohttp import web

from .common import Method
from .context import Context

@dataclass
class RouteHolder:
    """Dataclass for holding route information until it is passed to a server"""
    func: Coroutine[[Context], web.Response]
    path: str
    method: Method
    cog: 'Cog' = None

    @property
    def split_path(self):
        return self.path.rstrip('/').split('/')[1:]

class CogMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        attrs['_routes'] = []
        attrs['__cog_name__'] = kwargs.pop('name', name)
        for attr_name, attr_value in attrs.copy().items():
            if isinstance(attr_value, RouteHolder):
                attrs['_routes'].append(attr_value)
                attrs[attr_name] = attr_value.func
        self = super().__new__(cls, name, bases, attrs)
        for cog_route in getattr(self, '_routes'):
            cog_route.cog = self
        return self

class Cog(metaclass=CogMeta):
    def __init__(self):
        for route in self._routes:
            route.func = getattr(self, route.func.__name__)
            route.cog = self
    def inject(self, server: 'HTTPServer'):
        for index, route in enumerate(self._routes, start=1):
            try:
                server.router.add_handler(route)
            except Exception as e:
                for to_undo in self._routes[:index]:
                    server.router.remove_route(to_undo.split_path)
                raise e

    def _eject(self, server: 'HTTPServer'):
        for route in self._routes:
            server.router.remove_route(route.split_path)


def route(path: str, method: Method):
    def route_dec(func):
        if not iscoroutinefunction(func):
            raise TypeError('handler for route must be a coroutine')
        return RouteHolder(func, path, method)
    return route_dec
