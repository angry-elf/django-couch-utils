
from couchdbcurl import Server, Document, ResourceConflict, ResourceNotFound
from django.conf import settings

import hashlib
import random

from translit import slugify

def db(name = None):
    """name is key in settings.COUCHDB. If None, returns default database"""
    
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
    
    chunk_size = 1000
    
    def __init__(self, db):
        self.documents = []
        self.db = db
        
        
    def append(self, document):
        self.documents.append(document)

        if len(self.documents) == self.chunk_size:
            self.push()


    def push(self):
        if self.documents:
            self.db.update(self.documents)
            self.documents = []
            

def all_docs(db, skip_design_docs = False):

    for row in view_iterator(db, '_all_docs'):
        if not (skip_design_docs and row.id.startswith('_design/')):
            yield row

def design_docs(db):
    return view_iterator(db, '_all_docs', startkey = "_design/", endkey = "_design0", include_docs = True)


def view_iterator(db, view, **kwargs):
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
    """Generate unique database document ID based on provided prefix and random suffix"""
    
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
    """Generate doc with unique ID, based on provided prefix and random suffix. Retries on duplicate"""
    
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
    
    def process_request(self, request):
        for dbname in settings.COUCHDB:
            setattr(request, dbname, db(dbname))
            request._db = db

        
        
