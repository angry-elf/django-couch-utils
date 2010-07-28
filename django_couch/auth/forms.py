from django_couch.admin.forms import CouchAdminForm
from django import forms
from django_couch.auth.models import User

class UserForm(CouchAdminForm):
    TYPE = 'user'
    PREFIX = 'u_'
    ID_FIELD = 'username'
    
    username = forms.CharField(max_length = 64)
    password = forms.CharField(max_length = 128)
    is_staff = forms.BooleanField(required = False)
    admin = forms.BooleanField(required = False)

    def save(self, *args, **kwargs):
        if not self.cleaned_data['password'].startswith('sha1'):
            user = User(self.initial)
            user.set_password(self.cleaned_data['password'])
            self.cleaned_data['password'] = user.password
        
        CouchAdminForm.save(self, *args, **kwargs)
