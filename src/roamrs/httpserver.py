"""This module provides the HTTPServer which is the core of the package
"""
import asyncio
import re

from enum import Enum
from typing import List, Callable, Dict

from aiohttp import web
from .extensions import Extension
from .services import Service
from .auth import TokenValidator
from .common import Method
from .context import Context
from .cog import Cog, RouteHolder

__all__ = (
    'HandlerExists',
    'RouteDoesNotExist',
    'Route',
    'Router',
    'HTTPServer'
)


class HandlerExists(Exception):
    """An Exception that is raised when trying to add a handler that already
    exists
    """

    def __init__(self, path, method, old_handler, new_handler):
        super().__init__()
        self.path = path
        self.method = method
        self.handlers = (old_handler, new_handler)

    def __repr__(self):
        return (f'method {self.method} at path {self.path} is already used '
                f'by handler {self.handlers[0]}, refusing to overwrite with '
                f'handler {self.handlers[1]}.')


class RouteDoesNotExist(Exception):
    """An exception that is raised when attempting to find a route that does
    not exist
    """

    def __init__(self, path_list):
        super().__init__()
        self.path_list = path_list

    def __repr__(self):
        return 'route at path {path_list} does not exist.'




class Route:
    """An object that represents an endpoint that can be potentionally accessed
    by a client request.

    Each route has a handlers for each of the different available HTTP methods.
    They also have children which are the routes that come after this one.
    For example:
    the endpoint '/a/b/c' has three routes. A which has the child b, which has
    the child c.

    As well as setting the path to a fixed value like 'users' you can also make
    it variable by passing a string such as '{user_id}' the handler will match
    any string passed to it and pass the strings value to the handlers
    'url_data' parameter.

    Parameters
    ----------
    path : str
        The endpoint that this route will be attributed to, this is only one
        section of a uri.

    Attributes
    ----------
    path : str
        The endpoint that this route is attributed to, this is only one section
        of a uri.
    variable : bool
        If this route accepts any string instead of a specific one.
    handlers : dict
        A dictionary of handlers indexed by the method you can access them
        with.
    children : list of :class:`Route`
        The list of routes that are under this route. They are the 'b' to this 'a'.
    variable_child : :class:`Route`
        A route can only have one variable route under it, this is where it is stored.
    """

    __slots__ = ('path', 'handlers', 'children', 'variable', 'variable_child')

    def __init__(self, path: str):
        if path != '':
            ROUTE_PATTERN = re.compile(r'([A-Za-z0-9]+)|{([A-Za-z0-9.\-_]+)}')
            match = ROUTE_PATTERN.match(path)
            if not match:
                raise ValueError(f'Invalid path "{path}" passed to route')
            term, var = match.groups()
            # This path looks like "some text" so it is not variable
            if term is not None:
                self.path = term
                self.variable = False
            # This path looks like "{some text}" so it is variable
            else:
                self.path = var
                self.variable = True
        # This is the root path (it's a bit weird)
        else:
            self.path = path
            self.variable = False
        self.handlers = {i: None for i in Method}
        self.children = []
        self.variable_child = None

    async def __call__(self, path_list: List[str], method: Method, ctx: Context) -> web.Response:
        method = Method(ctx.raw_request.method)
        # If the remaining path list is empty then we must want this route!
        if path_list == []:
            if self.handlers[method]:
                # let's get our result from our handler
                return await self.handlers[method](ctx)
            # uh oh! we don't have a handler for this method
            raise web.HTTPNotFound()
        # The path list isn't empty so the next section sould
        # be a child right?
        for child in self.children:
            if path_list[0] == child.path:
                # Hey the path matches! let's get the result from the child.
                return await child(path_list[1:], method, ctx)
        # There wasn't a matching path? well is there a child we have that's
        # variable?
        if self.variable_child:
            # Let's update the url_data parameter with this path.
            ctx.url_data[self.variable_child.path] = path_list[0]
            return await self.variable_child(path_list[1:], method, ctx)
        # Wait there isn't a variable child either? Then what is the client
        # requesting?
        raise web.HTTPNotFound()

    def add_route(self, path_list: List[str]) -> 'Route':
        """Add a child route to this route. This creates any child routes
        nescesary to add the route you want to add.

        Don't know why you would do this, the router does this for you.

        Parameters
        ----------
        path_list : list of str
            The uri sections to add, the last one is the actual route you want
            to add.

        Returns
        -------
        :class:`Route`
            The route you added

        Raises
        ------
        ValueError
           If you try to add a variable child to this route when it already
           has one
        """
        # Hey the path list is empty, that means me right?
        if path_list == []:
            return self
        # The path list is not empty, maybe a child has the next section?
        for child in self.children:
            if child.path == path_list[0]:
                # This child does!
                return child.add_route(path_list[1:])
        # Does the endpoint belong under our variable child?
        if self.variable_child and (
                self.variable_child.path == path_list[0].strip('{}')):
            return self.variable_child.add_route(path_list[1:])
        # No, so let's add a new child to put the child under
        new_child = Route(path_list[0])
        if new_child.variable:
            if not self.variable_child:
                self.variable_child = new_child
            else:
                # The new child is variable but we already have a
                # variable child. wait...that's illegal.
                raise ValueError('Route already has a variable child')
        else:
            self.children.append(new_child)
        return new_child.add_route(path_list[1:])

    def add_handler(self, holder: RouteHolder):
        """Add a handler to a route under a given method

        Parameters
        ----------
        method : :class:`Method`
            The method that this handler can be accessed with
        handler : callable
            The coroutine that we want to add

        Returns
        -------
        None

        Raises
        ------
        :class:`HandlerExists`
            A handler already exists under this method, you can't replace it.
        """
        if self.handlers[holder.method] is not None:
            raise HandlerExists(
                self.path,
                holder.method,
                self.handlers[holder.method],
                holder.func)
        self.handlers[holder.method] = holder.func

    def remove_route(self, path_list: List[str]) -> bool:
        if len(path_list) == 1:
            for i, c in enumerate(self.children):
                if c.path == path_list[0]:
                    del self.children[i]
                    return True
            return False
        for i, child in enumerate(self.children):
            if child.path == path_list[0]:
                r = child.remove_route(path_list[1:])
                if r:
                    c = len(child.children) == 0
                    h = all(map(lambda h: h == None, child.handlers.values()))
                    if c and h:
                        del self.children[i]
                return True
        if self.variable_child and (
                self.variable_child.path == path_list[0].strip('{}')):
            self.variable_child = None
            return True
        return False

    def get_route(self, path_list: List[str]) -> 'Route':
        """Get a route from a list of endpoints

        Parameters
        ----------
        path_list : list of str
            The list of endpoints that we will find our route under

        Returns
        -------
        Route
            The route requested

        Raises
        ------
        :class:`RouteDoesNotExist`
        """
        if path_list == []:
            return self
        for child in self.children:
            if path_list[0] == child.path:
                return child.get_route(path_list[1:])
        if self.variable_child:
            return self.variable_child.get_route(path_list[1:])
        raise RouteDoesNotExist(path_list)


class Router:
    """The router redirects all requests to their handlers and stores the
    root route.

    You can either create your route yourself or let the HTTPServer do it for
    you.

    Parameters
    ----------
    services
        The services that will available to handlers (and the router)

    Attributes
    ----------
    base : :class:`Route`
        The root route that all requests are directed to.
    services : :class:`dict`
        The services that are available to handlers (and the router)
    """

    def __init__(self, services: Dict[str, object], extensions: Dict[str, Extension]):
        self.base = Route('')
        self.services = services
        self.extensions = extensions

    async def __call__(self, request: web.BaseRequest) -> web.Response:
        # This works as the first term in the and is evaluated before the
        # second. If the first term evalutes to false, the second term is
        # not evaluated at all
        token_validator =  self.services.get('roamgg_token')
        if token_validator and await token_validator(request.headers['Authorization']):
            split_url = self.split_url(request.path)
            if split_url[0] == '':
                user = await token_validator.get_user(request.headers['Authorizaiton'])
                if request.content_type == 'application/json':
                    data = await request.json()
                else:
                    data = request.query
                context = Context(request, user, {}, self.services, self.extensions, data)
                return await self.base(split_url, Method(request.method), context)
            # this should never happen. How does our url not start at the root?
            raise ValueError('wut?')
        raise web.HTTPUnauthorized()

    def add_route(self, url: str) -> Route:
        """Add a route, like the add route method of the :class:`Route`,
        except takes an url as one string like : '/a/b/c'

        Parameters
        ----------
        url : str
           The url to add a route for

        Returns
        -------
        Route
           The newly created route

        Raises
        ------
        ValueError
            This should never be raised, but if it is please raise an issue on
            github
        """
        split_url = self.split_url(url)
        if split_url[0] == '':
            return self.base.add_route(split_url[1:])
        # this should never happen
        raise ValueError('wut?')

    def remove_route(self, path: List[str]) -> bool:
        """Remove the route at the end of a route path,
        if no children or handlers are left, the parent is also removed

        Parameters
        ----------
        path : list of str
           The path to remove the route from

        Returns
        -------
        bool
           True if the route existed and was removed, false if it didn't exist
        """
        return self.base.remove_route(path)

    def add_handler(self, holder: RouteHolder):
        """Add a handler to a route at a given url
        This method creates routes as needed to add the handler.

        Parameters
        ----------
        url : str
            The url add the handler under
        method
            When the request has the method `method` use this handler

        Returns
        -------
        None
        """
        split_url = holder.split_path
        try:
            route = self.base.get_route(split_url)
        except RouteDoesNotExist:
            route = self.base.add_route(split_url)
        route.add_handler(holder)

    @staticmethod
    def split_url(url):
        """split a given url into a list of parts seperated by a '/'
        This removes an ending slash but not the begginning one as this is the
        root route's path
        """
        return url.rstrip('/').split('/')


class HTTPServer:
    """A class that runs an aiohttp server and contains all the server
    information.

    Parameters
    ----------
    services
        A list of services that will be available to the handlers and
        the router.
    router : :class:`Router`
        The router to use for this server.
    host : str
        The IP address to listen to requests on '0.0.0.0' for all locations.
    port : int
        The port to listen to requests on.

    Attributes
    ----------
    router : Router
        The router that this server uses.
    """

    def __init__(self,
                 services: Dict[str,
                                Service],
                 extensions: Dict[str, Extension],
                 host='0.0.0.0',
                 port=8080, security_url=None):
        for name, ext in extensions.items():
            if not isinstance(ext, Extension):
                raise TypeError(f"{name}: {ext} is not an instance of Extension")
        self.extensions = extensions
        if security_url:
            if 'roamgg_token' in services:
                raise ValueError('Can\'t enable security service as it is already registered')
            else:
                services['roamgg_token'] = TokenValidator.service_factory(security_url)
        self.services = {k: s(self.extensions) for k, s in services.items()}
        self.router = Router(self.services, self.extensions)
        self._host = host
        self._port = port
        self._exit_event = asyncio.Event()
        self.cogs = []

    async def __call__(self):
        server = web.Server(self.router)
        runner = web.ServerRunner(server)
        await runner.setup()
        site = web.TCPSite(runner, self._host, self._port)

        for extension in self.extensions.values():
            await extension(self.services, self.extensions)
        await site.start()
        print(f'Started HTTPServer on http://{self._host}:{self._port}/')
        # Keep running the server until the exit coroutine is used
        await self._exit_event.wait()

    async def exit(self):
        """Stop the server from running
        """
        for extension in self.extensions:
            await extension.stop()
        self._exit_event.set()

    def load_cog(self, cog: Cog):
        cog.inject(self)
        self.cogs.append(cog)

    def unload_cog(self, cog_name: str):
        for cog in self.cogs:
            if cog.__cog_name__ == cog_name:
                cog._eject(self)
