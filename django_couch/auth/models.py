from datetime import datetime
from couchdbcurl.client import Document


class User(Document):

    def is_active(self):
        """Fake function. Always returns True"""
        return True

    def is_authenticated(self):
        """Links to self.is_superuser"""
        return self.is_superuser

    def is_staff(self):
        """Fake function. Always returns True"""
        return True

    def get_and_delete_messages(self):
        return None


    def has_module_perms(self, module):
        pass

    def save(self, *args, **kwargs):
        """Save user object and update ``last_login`` field"""
        
        if hasattr(self, 'backend'):
            backend = self.backend
            del(self.backend)
        else:
            backend = None
            
        if hasattr(self, 'last_login') and type(self.last_login) == datetime:
            from django.conf import settings
            self.last_login = self.last_login.strftime(settings.DATETIME_FMT)

        Document.save(self, *args, **kwargs)

        if backend:
            self.backend = backend

    def set_password(self, raw_password):
        """This is copy-paste from django.contrib.auth.models.User.set_password()"""
        
        import random
        from django.contrib.auth.models import get_hexdigest
        
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)
        
        
