.. _services:

.. currentmodule:: roamrs

Services
========

Sometimes handlers and cogs just aren't enough.
When this is true, a Service may help.

Services are classes available to all handlers.
These services provide extra functionality to the server.
They must implement the `__call__` method which means they behave similarly to functions.

Here is an example Service to generate uuids when asked.

.. code-block:: python3

   import roamrs
   import uuid

   class UUIDService(roamrs.Service):
        def __init__(self, extensions, services):
                self.extensions = extensions
                self.services = services

        def __call__(self):
                return str(uuid.uuid4())

Services can obviously be more complex than this.
For a good example look at the :class:`.auth.TokenValidator` service.

Authorization Services
----------------------

the :class:`.httpserver.HTTPServer` is designed to allow you to easily add
authorization to your server. All you need to do is create a service from the
:class:`.services.AuthService` abstract class and the HTTPServer will detect and use it to authorize a user.
It will also attempt to use it to get the user details from the service.

The Roamrs package provides you with a prebuilt authorization service called
:class:`.auth.TokenValidator`. This service is designed to work with Roam.gg's
authorization server.

Technical considerations
------------------------

Some things to consider:

- Your `__init__` method must have it's first two arguments be the server's extensions and services.
- When initializing your service, you should pass the extension and service arguments, the HTTPServer will do this for you.
- If you attempt to interfere with the Service you will find that the variable it is stored under
  is not the class itself, but a ServiceHolder. This is how the HTTPServer initializes the Services.
  They are basically fancy partial functions.
- Because the ServiceHolders are "fancy" they still allow you to subclass your Services, just subclass the holder and it'll change it
  to subclass the service it holds.
