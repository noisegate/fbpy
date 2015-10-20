.. fbpy documentation master file, created by
   sphinx-quickstart on Fri Jun 20 01:39:00 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to fbpy's documentation!
================================

Contents:

.. toctree::
   :maxdepth: 2


General description
===================

The `fbpy` module is an API for drawing in the framebuffer on Linux machines.
It was conceived as part of an audio player project based on the
raspberry pi computer and wolfson pi audio interface. I needed a low-level
graphics library for visualizing audio data (scope, phase,...). I also
wanted to gain some programming skills, like writing c libs for python and
some kernel stuff. So this module is by no means an attempt to make a 
better graphics lib with fancy hardware acceleration or anythin or 
making something original. I think it is use able though and by examining 
the source, it might serve as a form of documentation if you want to
make something like this yourself. That is why I publish it. Oh, and of course
because I support open source hardware *and* software, the 'firmware' of
my audio player should be available as source :)

Website
-------

http://transistorlove.wordpress.com


Module documentation
====================

.. automodule:: fb
   :members:  

.. automodule:: svg
   :members:

.. automodule:: sprite
   :members:

.. automodule:: audioscope
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

