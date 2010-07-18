from django.contrib.admin.sites import AdminSite
from django.conf.urls.defaults import patterns, url, include
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy, ugettext as _
from django.utils.text import capfirst
from django.conf import settings
from forms import AdminForm
import os

class CouchdbAdminSite(AdminSite):
    index_template = 'couch_admin/index.html'
    
    def __init__(self):
        self._models = {}
        self.app_name = 'admin'
        self.name = 'admin'

    def index(self, request):
        app_list = self._models.values() #[{'name': self._models[key], 'models': self._models[key]['models']} for key in self._models]
        return render_to_response('couch_admin/index.html', {'app_list': app_list})
    
    def register(self, app, doc, admin_object):
        print 'register:', app, doc, admin_object
        app_url = app
        model_url = '%s/%s/' % (app_url, doc)
        if not app in self._models:
            self._models[app] = {
                'name': app,
                'app_url': app_url,
                'models': [],
                }
            
        self._models[app]['models'].append({
            'admin_url': model_url,
            'doc': doc,
            'name': doc,
            'admin': admin_object,
            'perms': {'change': True, 'add': True},
        })

    def get_urls(self):
        
        
        urlpatterns = patterns('',
            url(r'^$', self.index),
            url(r'^(?P<app>\w+)/$', 'django_couch.admin.app_index'),
            url(r'^(?P<app>\w+)/(?P<model>\w+)/$', 'django_couch.admin.items'),
            url(r'^(?P<app>\w+)/(?P<model>\w+)/(?P<action>add)/$', 'django_couch.admin.item_add'),
            url(r'^(?P<app>\w+)/(?P<model>\w+)/(?P<key>\w+)/delete/$', 'django_couch.admin.item_delete'),
            url(r'^(?P<app>\w+)/(?P<model>\w+)/(?P<key>\w+)/$', 'django_couch.admin.item_edit'),
        )
        ## for app in self._models:
        ##     for model in self._models[app]['models']:
        ##         urlpatterns += patterns('',
        ##                                 url(r'^%s/%s/' % (app, model['doc']), self.app_index) #'django_couch.admin.items')
        ##         )
        return urlpatterns

def app_index(self, app):
    
    return render_to_response('admin/app_index.html',
                              {
                                  'app_list': [site._models[app]],
                                  'title': _('%s administration') % capfirst(app),
                                  'admin_url': '%s/' % app
                                })

def items(self, app, model):
    class Fake2:
        pk = None

    class FakeList(list):
        pass
    
    class Fake1:
        result_count = 10
        full_result_count = 10
        date_hierarchy = None
        lookup_opts = [Fake2(), Fake2()]
        list_display = FakeList()
        formset = None
        result_list = FakeList()
        paginator = None
        page_num = None
        show_all = None
        multi_page = None
        can_show_all = None
        
    m = None
    for i in site._models[app]['models']:
        print i['name']
        if i['name'] == model:
            m = i
            break

    return render_to_response('admin/change_list.html',
                              {
                                  'cl': Fake1(),
                                  'app_list': [site._models[app]],
                                  'has_add_permission': True,
                                  'results': [{'key': 123, 'value': 456}, {'key': 'aaaaa', 'value': 'bbbbbb'}, {'key': 'aaaaa', 'value': 'bbbbbb'}, {'key': 'aaaaa', 'value': 'bbbbbb'}, {'key': 'aaaaa', 'value': 'bbbbbb'}]
                                })
    

def item_edit(request, app, model, key = None, action = None):
    print 'item_edit', app, model, key, action
    class Fake1:
        def get_ordered_objects(self):
            return []

    class Fieldsets(list):
        prepopulated_fields = []
        
    class Fieldset(list):
        name = 'fieldset'
        
    context = {
        'opts': Fake1(),
        'change': None,
        'is_popup': None,
        'save_as': {},
        'has_delete_permission': True,
        'show_delete': True,
        'has_add_permission': True,
        'has_change_permission': True,
        'add': True,
        'adminform': Fieldsets([Fieldset([AdminForm()])]),
    }
    return render_to_response('admin/change_form.html', context)


def item_delete(request, app, model, key):
    print 'item_delete', app, model, key
    pass

    

site = CouchdbAdminSite()

OUR_ROOT = os.path.realpath(os.path.dirname(__file__))
template_dir = os.path.join(OUR_ROOT, 'templates')

settings.TEMPLATE_DIRS = list(settings.TEMPLATE_DIRS) + [template_dir]
