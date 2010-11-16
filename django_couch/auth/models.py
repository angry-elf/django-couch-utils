from datetime import datetime
from couchdbcurl.client import Document
from django.conf import settings

from django.contrib.auth.models import get_hexdigest

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
            del(self.backend)
        else:
            backend = None
            
        if hasattr(self, 'last_login') and type(self.last_login) == datetime:
            self.last_login = self.last_login.strftime(settings.DATETIME_FMT)

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
        
        
