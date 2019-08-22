from dataclasses import dataclass
from aiohttp import web
from typing import Dict, Any

from .services import Service
from .extensions import Extension

@dataclass
class Context:
    raw_request: web.BaseRequest
    url_data: Dict[str, str]
    services: Dict[str, Service]
    extensions: Dict[str, Extension]
    sent_data: Dict[str, str]
    user_data: Dict[str, Any] = None

    @staticmethod
    def respond(data: Dict[str, Any]) -> web.Response:
        return web.json_response(data)
