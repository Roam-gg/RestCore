from enum import Enum
from aiostream import stream
from aiostream.core import Stream

class Method(Enum):
    """An enum of possible methods that handlers can respond to
    """

    GET = 'GET'
    POST = 'POST'
    PATCH = 'PATCH'
    DELETE = 'DELETE'

async def async_map(func, items):
    if isinstance(items, Stream):
        return stream.map(items, func)
    return stream.map(stream.iterate(items), func)

async def async_all(items):
    if isinstance(items, Stream):
        xs = items
    else:
        xs = stream.iterate(items)
    async with xs.stream() as streamer:
        async for item in streamer:
            if not item:
                return False
        return True
