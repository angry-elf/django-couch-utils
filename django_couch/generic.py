from annoying.decorators import render_to
from django.shortcuts import render_to_response
import django_couch

from json import loads

def docs_list(request, *args, **kwargs):
    db_key = kwargs.get('db_key')
    template = kwargs.get('template')
    view_args = kwargs.get('view_args', {}).copy()
    view = kwargs.get('view')
    
    db = django_couch.db(db_key)
    
    # some magic here
    if 'startkey' in view_args:
        view_args['startkey'] = loads(view_args['startkey'] % kwargs)
        
    if 'endkey' in view_args:
        view_args['endkey'] = loads(view_args['endkey'] % kwargs)

    
    view_res = db.view(view, **view_args)
    rows = view_res.rows
    
    
    
    return render_to_response(template, {'rows': rows, 'kwargs': kwargs})
