"""This module provides the jwtservice that can be used to verify jwt tokens
It uses PyJWT"""
import jwt
from .services import Service

class TokenInvalid(Exception):
    """A generic exception that is raised when a token is invalid
    """
    def __init__(self, token):
        super().__init__()
        self.token = token

    def __repr__(self):
        return f'The token {self.token} is not valid'

class JWTService(Service):
    """An object that decodes and verifies jwt tokens,
    simply call an instance of the class.

    Parameters
    ----------
    key : str
        The key to use, this can be any valid PyJWT key.
    algoritms : list of str
        The algorithms to try, this can be any valid PyJWT algoritms.
        For best security only enter algoritms you know you will be decoding.
    """
    __slots__ = ('key', 'algorithms')

    def __init__(self, key, algorithms, *args, **kwargs):
        self.key = key
        self.algorithms = algorithms

    def __call__(self, token, *args, **kwargs):
        try:
            return jwt.decode(
                token,
                *args,
                self.key,
                algorithms=self.algorithms,
                **kwargs)
        except jwt.exceptions.InvalidTokenError:
            raise TokenInvalid(token)

    def decode(self, token, *args, **kwargs):
        """decode a given token, additional args and kwargs
        from PyJWT can be passed
        """
        return self(token, *args, **kwargs)
