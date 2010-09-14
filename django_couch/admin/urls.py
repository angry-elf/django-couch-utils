from django.conf.urls.defaults import *
from django_couch.admin.views import *
from django.conf import settings

_patterns = [
    url(r'^crud/(?P<app>.+)/(?P<doc_type>.+)/(?P<doc_id>.+)/(?P<filename>.+)/attachment/$', attachment, name = 'attachment'),
    url(r'^crud/(?P<app>.+)/(?P<doc_type>.+)/(?P<doc_id>.+)/(?P<filename>.+)/attachment/delete/$', attachment_delete, name = 'attachment_delete'),
    url(r'^crud/(?P<app>.+)/(?P<doc_type>.+)/(?P<doc_id>.+)/delete/$', document_delete, name='document_delete'),
    url(r'^crud/(?P<app>.+)/(?P<doc_type>.+)/add/$', document, name='document_add'),
    url(r'^crud/(?P<app>.+)/(?P<doc_type>.+)/(?P<doc_id>.+)/$', document, name='document'),
    url(r'^crud/(?P<app>.+)/(?P<doc_type>.+)/$', documents, name='documents'),
    url(r'^crud/(?P<app>.+)/$', app, name='app'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name' : 'admin/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/'}, name='logout'),
    url('^$', root, name='root'),
]

for app in settings.INSTALLED_APPS:
    m = __import__(app, globals(), locals(), ['admin'], -1)
    if hasattr(m, 'admin') and hasattr(m.admin, 'urls'):
        _patterns.extend([i['url'] for i in m.admin.urls])


urlpatterns = patterns(
    '',
    *_patterns
)


