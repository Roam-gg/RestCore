import asyncio
from aiohttp import web
import re

from enum import Enum
from typing import List, Callable, Dict
from roamrs._jwt import JWTService, TokenInvalid


__all__ = (
    'HandlerExists',
    'RouteDoesNotExist',
    'Method',
    'Route',
    'Router',
    'HTTPServer'
)

def check_auth(request, jwt_service) -> bool:
    token = request.headers.get('Authorization')
    if not token:
        return False
    try:
        jwt_service(token)
    except TokenInvalid:
        return False
    else:
        return True

class HandlerExists(Exception):
    def __init__(self, path, method, old_handler, new_handler):
        self.path = path
        self.method = method
        self.handlers = (old_handler, new_handler)

    def __repr__(self):
        return (f'method {self.method} at path {self.path} is already used '
                f'by handler {self.handlers[0]}, refusing to overwrite with '
                f'handler {self.handlers[1]}.')


class RouteDoesNotExist(Exception):
    def __init__(self, path_list):
        self.path_list = path_list

    def __repr__(self):
        return 'route at path {path_list} does not exist.'


class Method(Enum):
    GET = 'GET'
    POST = 'POST'


class Route(object):
    __slots__ = ('path', 'handlers', 'children')

    def __init__(self, path):
        self.path = path
        self.handlers = {i: None for i in Method}
        self.children = []

    async def __call__(
            self, method: Method, request: web.BaseRequest,
            services: List[object],
            *args, **kwargs):
        if self.handlers[method] is None:
            raise web.HTTPNotFound()
        return await self.handlers[method](request, services, *args, **kwargs)

    def add_route(self, path_list: List[str]) -> None:
        if path_list == []:
            return None
        for child in self.children:
            if child.path == path_list[0]:
                return child.add_route(path_list[1:])
        new_child = Route(path_list[0])
        self.children.append(new_child)
        return new_child.add_route(path_list[1:])

    def add_handler(self, method: Method, handler: Callable[[
            web.BaseRequest, Dict[str, object]], web.Response]):
        if self.handlers[method] is not None:
            raise HandlerExists(
                self.path,
                method,
                self.handlers[method],
                handler)
        else:
            self.handlers[method] = handler

    def get_route(self, path_list: List[str]) -> 'Route':
        if path_list == []:
            return self
        for child in self.children:
            if path_list[0] == child.path:
                return child.get_route(path_list[1:])
        raise RouteDoesNotExist(path_list)


class Router(object):
    def __init__(self, services: Dict[str, object]):
        self.base = Route('')
        self.services = services

    async def route(self, request: web.BaseRequest):
        if check_auth(request, services['jwt']):
            split_url = self.split_url(request.path)
            if split_url[0] == '':
                route = self.base.get_route(split_url[1:])
                if route is None:
                    raise web.HTTPNotFound()
                else:
                    return await route(Method[request.method], request, self.services)
                # this should never happen
                raise ValueError('wut?')
        else:
            raise web.HTTPUnathorized()

    def add_route(self, url: str):
        split_url = self.split_url(url)
        if split_url[0] == '':
            self.base.add_route(split_url[1:])
        # this should never happen
        raise ValueError('wut?')

    def add_handler(
            self, url: str, method: Method,
            handler: Callable[[web.BaseRequest], Dict[str, object]]):
        split_url = self.split_url(url)[1:]
        try:
            route = self.base.get_route(split_url)
        except RouteDoesNotExist:
            self.base.add_route(split_url)
            route = self.base.get_route(split_url)
        route.add_handler(method, handler)

    @staticmethod
    def split_url(url):
        return url.rstrip('/').split('/')


class HTTPServer(object):
    def __init__(self,
                 services: Dict[str,
                                object],
                 router=None,
                 host='0.0.0.0',
                 port=8080):
        self.router = router if router else Router(services)
        self.host = host
        self.port = port
        self.exit_event = asyncio.Event()

    async def __call__(self):
        self._server = web.Server(self.router.route)
        self._runner = web.ServerRunner(self._server)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self.host, self.port)
        await site.start()
        print(f'Started HTTPServer on http://{self.host}:{self.port}/')
        await self.exit_event.wait()

    async def exit(self):
        self.exit_event.set()
