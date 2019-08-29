from .services import AuthService
from aiohttp import ClientSession
from typing import Any, Dict

class TokenValidator(AuthService):
    __slots__ = ('url')
    def __init__(self, url, *args, **kwargs):
        self.url = url.rstrip('/')
        self.__session = ClientSession(*args, **kwargs)

    async def __call__(self, auth_str: str) -> bool:
        async with self.__session.get(self.url+'/verify', headers={'Authorization': auth_str}) as resp:
            if resp.status == 200:
                return True
            if resp.status == 401:
                return False
            return False

    async def get_user(self, auth_str: str) -> Dict[str, Any]:
        async with self.__session.get(self.url+'/get_user', headers={'Authorization': auth_str}) as resp:
            if resp.status == 200:
                return await resp.json()
            if resp.status == 401:
                return None
            return None
