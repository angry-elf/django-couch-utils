
import django_couch
from couchdb.client import Document
from django.conf import settings

from django.contrib.auth.models import check_password, get_hexdigest
from django.contrib.auth import login
from datetime import datetime

class User(Document):

    def is_active(self):
        """Fake function"""
        return True

    def is_authenticated(self):
        """Fake function"""
        return True

    def get_and_delete_messages(self):
        return None


    def has_module_perms(self, module):
        pass

    def save(self, *args, **kwargs):
        if hasattr(self, 'backend'):
            backend = self.backend
        else:
            backend = None
            
        self.last_login = self.last_login.strftime(settings.DATETIME_FMT)
        del(self.backend)
        Document.save(self, *args, **kwargs)

        if backend:
            self.backend = backend

    def set_password(self, raw_password):
        """This is copy-paste from django.contrib.auth.models.User.set_password()"""
        
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)
        
        
    
class CouchBackend(object):

    def __init__(self):
        self.db = django_couch.db(settings.COUCHDB_AUTH_DB)

    def get_user(self, user_id):
        print 'get_user'
        return User(self.db[user_id], _db = self.db)


    def authenticate(self, username, password):
        print 'auth'
        rows = self.db.view(settings.COUCHDB_AUTH_VIEW, key = username.lower(), include_docs = True, limit = 1).rows
        if len(rows) and check_password(password, rows[0].value):
            print 'here0', rows[0].doc
            print 'here', User(rows[0].doc, db = self.db)
            return User(rows[0].doc, _db = self.db)
        pass

    
