from django_couch.admin.forms import CouchAdminForm
from django import forms

class FlatpageForm(CouchAdminForm):
    TYPE = 'page'
    PREFIX = 'p_'
    ID_FIELD = 'title'
    
    title = forms.CharField(max_length = 255)
    url = forms.CharField(max_length = 255)
    keywords = forms.CharField(max_length = 64000, required = False)
    description = forms.CharField(max_length = 64000, required = False)
    text = forms.CharField(max_length = 256000, required = False, widget = forms.Textarea(attrs = {'cols': 80, 'rows': 20}))
    date = forms.CharField(max_length = 32)
    
