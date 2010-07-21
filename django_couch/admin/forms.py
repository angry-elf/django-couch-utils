from django import forms
import django_couch
from django_couch.translit import slugify

class CouchAdminForm(forms.Form):
    TYPE = None
    PREFIX = None
    ID_FIELD = None
    
    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        if not self.TYPE or not self.PREFIX or not self.ID_FIELD:
            raise Exception('Please, specify TYPE, PREFIX and ID_FIELD in your form class')
    
    def save(self):
        self.initial.update(self.cleaned_data)
        
        if not self.initial.get('_id'):
            self.initial.type = self.TYPE
            self.initial.create('%s%s' % (self.PREFIX, slugify(self.cleaned_data[self.ID_FIELD])))
        else:
            self.initial.save()
            
    
