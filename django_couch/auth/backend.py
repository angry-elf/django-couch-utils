
import django_couch
from django.conf import settings

from django.contrib.auth.models import check_password, get_hexdigest
from django_couch.auth.models import User
    
class CouchBackend(object):

    def __init__(self):
        self.db = django_couch.db(settings.COUCHDB_AUTH_DB)

    def get_user(self, user_id):
        return User(self.db[user_id], _db = self.db)


    def authenticate(self, username, password):
        rows = self.db.view(settings.COUCHDB_AUTH_VIEW, key = username.lower(), include_docs = True, limit = 1).rows
        
        if len(rows) and check_password(password, rows[0].value):
            return User(rows[0].doc, _db = self.db)
        pass

    
