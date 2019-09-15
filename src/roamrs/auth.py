from .services import AuthService
from aiohttp import ClientSession
from typing import Any, Dict

class TokenValidator(AuthService):
    __slots__ = ('url')
    def __init__(self, _, __, url, *args, **kwargs):
        self.url = url.rstrip('/')
        self.__args = args
        self.__kwargs = kwargs
        self.__session = None

    async def _create_session(self):
        if not self.__session:
            self.__session = ClientSession(*self.__args, **self.__kwargs)

    async def __call__(self, auth_str: str) -> bool:
        await self._create_session()
        async with self.__session.get(self.url+'/verify', headers={'Authorization': auth_str}) as resp:
            if resp.status == 200:
                return True
            if resp.status == 401:
                return False
            return False

    async def get_user(self, auth_str: str) -> Dict[str, Any]:
        await self._create_session()
        async with self.__session.get(self.url+'/get_user', headers={'Authorization': auth_str}) as resp:
            if resp.status == 200:
                return await resp.json()
            if resp.status == 401:
                return None
            return None
