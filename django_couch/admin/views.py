from django_couch.admin import Admin

from annoying.decorators import render_to
from django.http import Http404

def _find_app(app_name):
    app_item = None
    for item in Admin().apps:
        if item['name'] == app_name:
            app_item = item
            break

    if not app_item:
        raise Http404('Undefined application')
    return app_item

def _find_doc_type(app_item, doc_type):
    doc_item = None
    for item in app_item['doc_types']:
        if item['type'] == doc_type:
            doc_item = item
            break
        
    if not doc_item:
        raise Http404('Undefined document type')

    return doc_item


@render_to('admin/root.html')
def root(request):
    admin = Admin()
    print admin.apps
    
    return {'apps': admin.apps}


@render_to('admin/app.html')
def app(request, app):

    app_item = _find_app(app)
    
    return {'app': app_item}


@render_to('admin/documents.html')
def documents(request, app, doc_type):
    app_item = _find_app(app)
    doc_item = _find_doc_type(app_item, doc_type)
    

    rows = request._db(app_item.get('db')).view(doc_item['view']).rows
    
    return {
        'app': app_item,
        'doc_type': doc_type,
        'rows': rows,
    }

@render_to('admin/document.html')
def document(request, app, doc_type, doc_id):
    app_item = _find_app(app)
    doc_item = _find_doc_type(app_item, doc_type)
    document = request._db(app_item.get('db'))[doc_id]
    
    return {
        'app': app_item,
        'doc_type': doc_type,
        'doc_id': doc_id,
        'document': document,
    }



def document_delete(request, app, doc_type, doc_id):
    pass


