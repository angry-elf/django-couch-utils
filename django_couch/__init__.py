
from couchdbcurl import Server, Document, ResourceConflict, ResourceNotFound
from django.conf import settings

import hashlib
import random

from translit import slugify

def db(name = None):
    """name is key in settings.COUCHDB. If None, returns default database.
    Examples::
    
      settings.COUCHDB = {
        'db1': {
          'server': 'http://node1:5984',
          'database': 'database1',
          'default' : True,
        },
        'db2': {
          'server': 'http://node1:5984',
          'database': 'database2',
        },
      }

    Next, you may access django databases as::

      import django_couch
      django_couch.db() # Default database (db1)
      django_couch.db('db1') # Database1 (key - db1) @ http://node1:5984/database1
      django_couch.db('db2') # Database2 (key - db2) @ http://node1:5984/database2

          
    
    """
    
    if not name:
        default = [key for key in settings.COUCHDB if settings.COUCHDB[key].get('default')]
        if len(default) != 1:
            raise Exception("There are no/multiple default database. Please, check settings.COUCHDB value.")
        name = default[0]
        
    server = Server(settings.COUCHDB[name]['server'])
    
    return server[settings.COUCHDB[name]['database']]

## server = Server(settings.COUCHDB_ADDR)

## db = server[settings.COUCHDB_NAME]

class Updater(object):
    """Bulk-updater helper.

    Example usage:

    ::

      updater = Updater(db)
      for document in documents:
          ... # some work here
          updater.append(document)

      updater.push() # last bulk push to ensure all documents are commited to database
    
    """
    chunk_size = 1000
    """Bulk pushes will be done when ``chunk_size`` documents are in queue"""
    
    def __init__(self, db):
        self.documents = []
        self.db = db
        
        
    def append(self, document):
        """Append document object to bulk queue"""
        self.documents.append(document)

        if len(self.documents) == self.chunk_size:
            self.push()


    def push(self):
        """Force push documents queue into database"""
        if self.documents:
            self.db.update(self.documents)
            self.documents = []
            

def all_docs(db, skip_design_docs = False):
    """Iterator-based function, returning all documents from database"""
    for row in view_iterator(db, '_all_docs'):
        if not (skip_design_docs and row.id.startswith('_design/')):
            yield row

def design_docs(db):
    """Iterator-based function, returning design-document from database"""
    return view_iterator(db, '_all_docs', startkey = "_design/", endkey = "_design0", include_docs = True)


def view_iterator(db, view, **kwargs):
    """Iterator helper. You may call this, when you need to iterate over a very large number of rows. This function will automatically split requests by 300 result rows, accurate handling ``start_docid``.

    Example::
    
      for row in view_iterator(db, 'very_large_result_set/will_produce_this_view'):
          ... # some work here
          
    
    """
    
    block_size = 300

    v = db.view(view, limit = block_size, **kwargs)
    while len(v.rows) > 1:
        for row in v.rows[:-1]:
            yield row

        start = v.rows[-1].key
        start_docid = v.rows[-1].id

        if 'startkey' in kwargs:
            del(kwargs['startkey'])

        kwargs['startkey'] = start
        if start_docid:
            kwargs['startkey_docid'] = start_docid
            
        v = db.view(view, limit = block_size, **kwargs)

        
    if len(v.rows):
        yield v.rows[0]


def generate_id(db, prefix, suffix_length = 12, id_string = '%s%s'):
    """Generate unique database document ID based on provided prefix and random suffix.
    **Deprecated since generate_doc() function**
    """
    
    rand = hashlib.sha1(str(random.random())).hexdigest()[:suffix_length]
    
    key = id_string % (prefix, '')
    max_retry = 1000
    
    while key in db:
        rand = hashlib.sha1(str(random.random())).hexdigest()[:suffix_length]
        key = id_string % (prefix, '_%s' % rand)
        max_retry -= 1

        if max_retry < 0:
            raise Exception("Retry-limit reached during document id generation")

    return key

def generate_doc(db, prefix, suffix_length = 12, id_string = '%s%s', max_retry = 100, data = {}):
    """Generate doc with unique ID, based on provided prefix and random suffix. Retries on duplicate.
    **Deprecated since couchdbcurl.client.Document.create() method.**
    """
    
    assert not '_id' in data
    assert not '_rev' in data
    assert max_retry > 0
    assert type(max_retry) == int
    
    #doc = data.copy()
    
    rand = hashlib.sha1(str(random.random())).hexdigest()[:suffix_length]
    doc_id = id_string % (prefix, '')
    
    while True:
        
        try:
            db[doc_id] = data
            break
        except ResourceConflict:
            pass
        
        max_retry -= 1
        if max_retry < 0:
            raise Exception("Retry-limit reached during document generation")
        
        rand = hashlib.sha1(str(random.random())).hexdigest()[:suffix_length]
        doc_id = id_string % (prefix, '_%s' % rand)
        

class CouchMiddleware:
    """Django middleware helper.
    Configuration::

      settings.MIDDLEWARE_CLASSES=(
      ...
      'django_couch.CouchMiddleware',
      )
      
      settings.COUCHDB = {
        'db1': {
          'server': 'http://node1:5984',
          'database': 'database1',
          'default' : True,
        },
        'db2': {
          'server': 'http://node1:5984',
          'database': 'database2',
        },
      }

    Next, you may access django databases as::
    
      def some_view(request):
          request.db1 # Database1 (key - db1) @ http://node1:5984/database1
          request.db2 # Database2 (key - db2) @ http://node1:5984/database2
          
          request._db() # Default database (db1)
          request._db('db1') # Database1
          request._db('db2') # Database2
          
      
      """
      
    def process_request(self, request):
        for dbname in settings.COUCHDB:
            setattr(request, dbname, db(dbname))
            request._db = db

        
        
