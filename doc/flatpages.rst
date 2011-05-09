Flatpages Middleware
====================

This is almost the same as default django.flatpages framework but using couchdb for pages storage.

Configuration
-------------
::

  settings.MIDDLEWARE_CLASSES=(
    ...
    'django_couch.flatpages.middleware.FlatpageFallbackMiddleware',
  )

  settings.INSTALLED_APPS=(
    ...
    'django_couch.flatpages',
    ...
  )

  COUCHDB_FLATPAGES = 'pages/list' # named view


For every 404 response, framework will call database view to get key == ``request.path``. So, function ```pages/list``` must be like::

  function(doc) {
      if (doc.type == 'page') {
          emit(doc.url, none);
      }
  } 

Document will be rendered into template ``static.html``. There will variable ``doc`` in template context.


Known limitations
-----------------

#. Database must be named as ``db`` in ``settings.COUCHDB`` hash
#. Template name will always be ``static.html``

Example
-------
Document::

  {
    "title": "Index page",
    "url": "/",
    "body": "This is index page body",
    "keywords": "some,keywords,here",
    "type": "page",
  }

Template (``static.html``):

.. sourcecode:: html

  <html>
      <head>
          <title>{{ doc.title }}</title>
          <meta name="keywords" content="{{ doc.keywords }}" />
      </head>
      <body>
          <h1>{{ doc.title }}</h1>
          {{ doc.body }}
      </body>
  </html>

