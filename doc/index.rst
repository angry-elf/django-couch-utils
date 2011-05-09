.. django-couch-utils documentation master file, created by
   sphinx-quickstart on Mon May  9 16:44:15 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-couch-utils's documentation!
==============================================

Contents:

Installation
============
::

  easy_install django-couch-utils

Hint
----

Default django behaviour is to store sessions in database. To eliminate this activity, use another storage engine, for example, file storage::

  settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'



API
===

.. toctree::
   :maxdepth: 2

   helpers
   authentication
   flatpages



Manage.py extensions
====================

.. toctree::
   :maxdepth: 2

   managepy



   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

