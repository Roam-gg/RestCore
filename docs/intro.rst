.. currentmodule:: roamrs

.. _intro:

Introduction
============

This is the documentation for roamrs, a library for python to
help in creating rest based applications (though it can do more
than that).

Prerequisites
-------------

roamrs works with Python 3.7.0 or higher. Support for earlier versions
of Python is not provided. Python 2.7 or lower is not supported. Python 3.4
or lower is not supported due to one of the dependicies (:doc:`aiohttp <aio:index>`)
not supporting Python 3.4.

.. _installing:

Installing
----------

You can get the library directly from PyPI: ::

    python3 -m pip install -U roamrs

You can install the latest development version directly from Github (No promises that it works): ::

    python3 -m pip install git+https://github.com/Roam-gg/RestCore.git@develop

Basic Concepts
--------------

roamrs uses routes to know what functions should be used to create the HTTP response.
You can register a route to a function using the server's  `add_route` decorator.

.. code-block:: python3

    import roamrs

    server = roamrs.HTTPServer()

    @server.add_route('/hello', roamrs.Method.GET)
    async def hello(ctx):
        return ctx.respond('Hello!', content_type='text/plain')

    server.run()
