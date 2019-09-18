.. _quickstart:

.. currentmodule:: roamrs

Quickstart
==========

This page gives a brief introduction to the library. It assumes you have the library installed,
if you don't check the :ref:`installing` section.

A Echo Server
----------------

Let's make a server that echo a message sent to it. It will also tell the user to send a POST
request, if they instead try to do get request.

It would look something like this:

.. code-block:: python3

   import roamrs

   server = roamrs.HTTPServer()


   @server.add_route("/echo", roamrs.Method.GET)
   async def get_echo(ctx):
       return ctx.respond("Try sending a post request", content_type="text/plain")


   @server.add_route("/echo", roamrs.Method.POST)
   async def post_echo(ctx):
       return ctx.respond(ctx.sent_data, content_type="text/plain")


   server.run()

Let's name this file ``echo_server.py``. Make sure not to name it ``roamrs.py`` as that'll conflict
with the library.

Let's walk through what's happening step by step, as there's a lot happening.

1. The first line imports the library. If this raises a `ModuleNotFoundError` or `ImportError`
   then go to the :ref:`installing` section to get the library installed correctly.
2. Next, an instance of the :class:`HTTPServer` is created. This httpserver is the base for all of your
   routes and does the actual routing and accepting of http requests.
3. We then use the :meth:`HTTPServer.add_route` dectorator to register a handler to a route.
   This dectorator takes the function and adds it to the tree of routes that can be served.
   How it does this is out of this scope and shouldn't be worried about unless you want to help develop.
4. Then we have our functions these are what the server runs to get the response to send to the client.
5. Then we tell our server to start running.

Now that we've made a server, we have to run it. This is simple with Python.

.. code-block:: shell

   $ python3 echo_server.py

Now that you have a working and running server. Why not try playing around with it. See if you can get it to echo json too.
