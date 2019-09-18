.. _extensions:

.. currentmodule:: roamrs

Extensions
==========

Services are great, but they don't allow you to run something in simulataniously,
like a websocket server. This is where extensions come in. Extensions are like services
in that they are passed to handlers and they can do things with them, but they are seperate
from the server and run continously in parrallel.

For example, an implementation of a small echo websocket extension could be:

.. code-block:: python3

   import roamrs
   import websocket
   import asyncio


   class WebSocketExtension(roamrs.Extension):
       def __init__(self, host, port):
           super().__init__()
           self.host = host
           self.port = port
           self._stop = asyncio.Event()
           self.services = None
           self.extensions = None
           self.server = None

       async def handler(self, websocket, path):
           msg = await websocket.recv()
           await websocket.send(msg)

       async def __call__(self, *args):
           self.server = asyncio.create_task(self._start())

       async def _start(self):
           async with websockets.serve(self.handler, self.host, self.port):
               await self._stop.wait()

       async def stop(self):
           self._stop.set()
           await self.server


   server = roamrs.HTTPServer(extensions={"ws": WebSocketExtension("127.0.0.1", 8081)})
   server.run()

The main difference between extensions and services is that the registered services and extensions
are injected into an extension in it's `__call__` method rather than it's `__init__` like services.
