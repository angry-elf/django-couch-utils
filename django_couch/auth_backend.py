
import django_couch
from django.conf import settings

from django.contrib.auth.models import check_password
from django.contrib.auth import login

class User(dict):

    @property
    def id(self):
        return self['_id']

    def is_active(self):
        """Fake function"""
        return True

    def is_authenticated(self):
        """Fake function"""
        return True

    def save(self, *args, **kwargs):
        """Another fake function"""
        pass

    def get_and_delete_messages(self):
        return None

    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            dict.__getattr__(self, key)
    
class CouchBackend(object):

    def __init__(self):
        self.db = django_couch.db(settings.COUCHDB_AUTH_DB)

    def get_user(self, user_id):
        return User(self.db[user_id])


    def authenticate(self, username, password):
        rows = self.db.view(settings.COUCHDB_AUTH_VIEW, key = username, include_docs = True, limit = 1).rows
        if len(rows) and check_password(password, rows[0].value):
            return User(rows[0].doc)
        pass

    
