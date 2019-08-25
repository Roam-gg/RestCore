from enum import Enum

class Method(Enum):
    """An enum of possible methods that handlers can respond to
    """

    GET = 'GET'
    POST = 'POST'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
