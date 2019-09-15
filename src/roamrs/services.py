from typing import Dict, Union, Optional, Any
import abc
import asyncio

class AbstractService(abc.ABC):
    @abc.abstractmethod
    def __init__(self, extensions, services, *args, **kwargs):
        pass

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        pass

class ServiceHolder:
    _CLASS_HELD = AbstractService
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def __call__(self, e, s):
        return self._CLASS_HELD(e, s, *self.args, **self.kwargs)

class ServiceMeta(abc.ABCMeta):
    def __new__(cls, name, bases, dct):
        if ServiceHolder in bases[-1].__mro__:
            new_bases = []
            for base in bases:
                if ServiceHolder in base.__mro__:
                    new_bases.append(base._CLASS_HELD)
                else:
                    new_bases.append(base)
            h = super(ServiceMeta, cls).__new__(cls, name, tuple(new_bases), dct)
        else:
            h = super(ServiceMeta, cls).__new__(cls, name, bases, dct)
        t = super(ServiceMeta, cls).__new__(cls, name+'Holder', (ServiceHolder,), {'_CLASS_HELD': h})
        return t

class Service(AbstractService, metaclass=ServiceMeta):
    _AUTH_SERVICE = False

    @property
    def is_auth_service(self):
        return self._AUTH_SERVICE

class AuthService(Service):
    _AUTH_SERVICE = True
