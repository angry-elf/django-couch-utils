from django_couch.admin import Admin

from annoying.decorators import render_to
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.conf import settings

from couchdbcurl.client import Document

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



@user_passes_test(settings.COUCHDB_AUTH_ADMIN_LAMBDA)
@render_to('admin/root.html')
def root(request):
    admin = Admin()
    #print admin.apps
    
    return {'apps': admin.apps}


@user_passes_test(settings.COUCHDB_AUTH_ADMIN_LAMBDA)
@render_to('admin/app.html')
def app(request, app):

    app_item = _find_app(app)
    
    return {'app': app_item}


@user_passes_test(settings.COUCHDB_AUTH_ADMIN_LAMBDA)
@render_to('admin/documents.html')
def documents(request, app, doc_type):
    app_item = _find_app(app)
    doc_item = _find_doc_type(app_item, doc_type)
    
    view = request._db(app_item.get('db')).view(doc_item['view'], descending = doc_item.get('descending', False))

    return {
        'app': app_item,
        'doc_type': doc_type,
        'total': view.total_rows,
        'rows': view.rows,
    }


@user_passes_test(settings.COUCHDB_AUTH_ADMIN_LAMBDA)
@render_to('admin/document.html')
def document(request, app, doc_type, doc_id = None):
    app_item = _find_app(app)
    doc_item = _find_doc_type(app_item, doc_type)
    if doc_id:
        document = request._db(app_item.get('db'))[doc_id]
    else:
        document = Document(_db = request._db(app_item.get('db')))
    
    
    form_class = doc_item.get('form')
    form = None
    
    if form_class:
        form = form_class(initial = document)
        
        if request.method == 'POST':
            form = form_class(request.POST, request.FILES, initial = document)
            if form.is_valid():
                form.save(files = request.FILES)
                return redirect('couchdb:documents', app, doc_type)

    
    document.attachments = document.get('_attachments', {})
    
    return {
        'app': app_item,
        'doc_item': doc_item,
        'doc_type': doc_type,
        'doc_id': doc_id,
        'document': document,
        'form': form,
    }



@user_passes_test(settings.COUCHDB_AUTH_ADMIN_LAMBDA)
@render_to('admin/document_delete.html')
def document_delete(request, app, doc_type, doc_id):
    app_item = _find_app(app)
    doc_item = _find_doc_type(app_item, doc_type)
    document = request._db(app_item.get('db'))[doc_id]

    if request.method == 'POST':
        document.delete()
        return redirect('couchdb:documents', app, doc_type)
    
    return {
        'app': app_item,
        'doc_type': doc_type,
        'doc_id': doc_id,
    }


@user_passes_test(settings.COUCHDB_AUTH_ADMIN_LAMBDA)
@user_passes_test(lambda u: getattr(u, 'admin', False))
def attachment(request, app, doc_type, doc_id, filename):
    app_item = _find_app(app)
    doc_item = _find_doc_type(app_item, doc_type)
    
    try:
        document = request._db(app_item.get('db'))[doc_id]
    except ResourceNotFound:
        raise Http404('Document not found')
    
    
    if filename in document.get('_attachments', {}):
        return HttpResponse(document.get_attachment(filename), mimetype = document._attachments[filename]['content_type'])
    else:
        raise Http404('File not found')

@user_passes_test(settings.COUCHDB_AUTH_ADMIN_LAMBDA)
@render_to('admin/attachment_delete.html')
def attachment_delete(request, app, doc_type, doc_id, filename):
    app_item = _find_app(app)
    doc_item = _find_doc_type(app_item, doc_type)
    
    try:
        document = request._db(app_item.get('db'))[doc_id]
    except ResourceNotFound:
        raise Http404('Document not found')

    
    if filename in document.get('_attachments', {}):
        if request.method == 'POST':
            document.delete_attachment(filename)
            return redirect('couchdb:document', app, doc_type, document.id)
    else:
        raise Http404('File not found')


    return {
        'app': app_item,
        'doc_item': doc_item,
        'doc_type': doc_type,
        'doc_id': doc_id,
        'document': document,
        'filename': filename,
        'file': document._attachments[filename]
    }
