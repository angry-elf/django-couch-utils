
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User as DjangoUser
from django_couch.auth.models import User

import django_couch
from couchdbcurl.client import ResourceConflict

class Command(BaseCommand):
    
    help = u'Creates admin user'
    
    def execute(self, db_key, username, *args, **kwargs):
        
        db = django_couch.db(db_key)
        skel = {
            'type': 'user',
            'is_staff': True,
            'is_superuser': True,
            'username': username,
        }
        
        u = User(skel, _db = db)
        password = DjangoUser.objects.make_random_password()
        u.set_password(password)
        #password_hash = u.password
        
        
        u.create('u_%s' % username)
        print 'User %s created. Document id: %s, password: %s' % (username, u.id, password)
        
        ## try:
        ##     db['u_%s' % username] = {"is_superuser": True, "is_staff": True, "last_login": None, "password": password_hash, "type": "user", "username": username}
        ##     print "User %s created. Password is: %s" % (username, password)
        ## except ResourceConflict:
        ##     print "Create user failed: conflict"
        
        
