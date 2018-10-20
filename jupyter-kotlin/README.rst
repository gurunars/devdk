jupyter-kotlin
==============

A docker image that allows you to use Kotlin instead of Python.

See `example <./Example.ipynb>`_ for more details

Usage
-----

Create and enter a project directory:

::

    mkdir notebook_project
    cd notebook_project


Run docker container inside:

::

    docker run -it --rm -v $PWD:/project -p 8888:8888 nephilimsolutions/jupiter-kotlin

Open `http://localhost:8888 <http://localhost:8888>`_ in a browser.