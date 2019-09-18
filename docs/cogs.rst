.. _cogs:

.. currentmodule:: roamrs

Cogs
====

Managing many handlers in one file can be hard, this is why the roamrs library has Cogs.
Cogs are classes that allow you to have handlers attached. You can load these cogs into
the server and it will add all the routes and handlers required. They can also be used to
make your webserver store states, allowing you to change responses based off of data stored
in the cog.

The summary of how cogs work is:

- Each cog is a Python class that subclasses :Class:`.cog.Cog`.
- Every handler is marked wuth the :func:`.cog.route` decorator.
- Cogs are then registered with a :meth:`.HTTPServer.load_cog` call.
- Cogs are deregistered with a :meth:`.HTTPServer.unload_cog` call.

Example
-------

This example cog adds a ``echo`` route to your server, with two handlers for GET and POST.
The purpose of the cog is to store a list of passed phrases. Each time a POST request is
made the body is added to the list. When a GET request is made, the first phrase is sent back.

.. code-block:: python3

   import roamrs

   class Echo(roamrs.Cog):
        def __init__(self):
             super().__init__()
             self.phrases = []

        @roamrs.route('/echo', roamrs.Method.GET)
        async def get_echo(self, ctx):
             if len(self.phrases) > 0:
                 text = self.phrases.pop(0)
             else:
                 text = 'N/A'
             return ctx.respond(text, content_type='text/plain')

        @roamrs.route('/echo', roamrs.Method.POST)
        async def post_echo(self, ctx):
             self.phrases.append(ctx.sent_data)
             return ctx.respond('OK', content_type='text/plain')

   server = roamrs.HTTPServer()
   server.load_cog(Echo())
   server.run()

A couple of things to consider when making cogs:

- All handlers must be marked with the :func:`.cog.route` decorator.
- The name of the cog is automatically derived from the class name but can be overriden.
- All handlers must now take an additional ``self`` parameter.
- You must call the ``__init__`` method of :class:`.cog.Cog` otherwise the handlers will not be
  correctly bound to the cog and therefore will not be called properly by the server.

Cog registration
----------------

Once you have defined your cogs, you need to tell the server to register the cogs to be used.
We do this via the :meth:`.httpserver.HTTPServer.load_cog` method.

.. code-block:: python3

    server.load_cog(Echo(server))

We reference cogs by name, so we can remove a cog by using the :meth:`.httpserver.HTTPServer.unload_cog` method.
Like so:

.. code-block:: python3

   server.unload_cog('Echo')

               
Using Cogs
----------

Just as we remove cogs by name, we can also retrieve them by name. This allows you to have intercommunication between your cogs.
You can access the cogs from the server instance stored in the context passed to your handlers. Or from the server instance passed into the cog upon initialization.
