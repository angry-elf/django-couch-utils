import os
from django.conf import settings
from pprint import pprint

MY_ROOT = os.path.realpath(os.path.dirname(__file__))

settings.TEMPLATE_DIRS = list(settings.TEMPLATE_DIRS) + [os.path.join(MY_ROOT, 'templates')]

class Admin(object):
    apps = []



def autodiscover():
    admin = Admin()
    for app in settings.INSTALLED_APPS:
        m = __import__(app, globals(), locals(), ['admin'], -1)

        if hasattr(m, 'admin'):
            doc_types = []
            urls = []
            if hasattr(m.admin, 'doc_types'):
                doc_types = m.admin.doc_types
                
            if hasattr(m.admin, 'urls'):
                urls = m.admin.urls

            if doc_types or urls:
                admin.apps.append({
                    'app': app,
                    'name': app[app.rfind('.') + 1:],
                    'doc_types': doc_types,
                    'urls': urls,
                })
            
            
