from django_couch.admin.forms import CouchAdminForm
from django import forms

class UserForm(CouchAdminForm):
    TYPE = 'user'
    PREFIX = 'u_'
    ID_FIELD = 'username'
    
    username = forms.CharField(max_length = 64)
    password = forms.CharField(max_length = 128)
    is_staff = forms.BooleanField(required = False)
    
        
