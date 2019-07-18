import jwt


class TokenInvalid(Exception):
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'The token {self.token} is not valid'


class JWTService(object):
    __slots__ = ('key', 'algorithms')

    def __init__(self, key, algorithms):
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
