from django.conf.urls.defaults import *
from django_couch.admin.views import *

urlpatterns = patterns(
        '',
        url('^(?P<app>.+)/(?P<doc_type>.+)/(?P<doc_id>.+)/delete/$', document_delete, name='document_delete'),
        url('^(?P<app>.+)/(?P<doc_type>.+)/(?P<doc_id>.+)/$', document, name='document'),
        url('^(?P<app>.+)/(?P<doc_type>.+)/$', documents, name='documents'),
        url('^(?P<app>.+)/$', app, name='app'),

        url('^$', root, name='root'),
)


