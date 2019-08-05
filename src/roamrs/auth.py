from .services import Service
from aiohttp import ClientSession

class TokenValidator(Service):
    __slots__ = ('url')
    def __init__(self, url, *args):
        self.url = url.rstrip('/')
        self.__session = ClientSession()

    async def __call__(self, token):
        async with self.__session.get(self.url+'/verify', headers={'Authorization': token}) as resp:
            if resp.status == 200:
                return True
            if resp.status == 401:
                return False
            return False

    async def get_user(self, token):
        async with self.__session.get(self.url+'/get_user', headers={'Authorization': token}) as resp:
            if resp.status == 200:
                return await resp.json()
            if resp.status == 401:
                return {}
            return {}
