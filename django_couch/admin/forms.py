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
    
    def save(self, files = None):
        self.initial.update(self.cleaned_data)
        
        if not self.initial.get('_id'):
            self.initial.type = self.TYPE
            if isinstance(self.ID_FIELD, list):
                id_field = slugify('-'.join([self.cleaned_data[s] for s in self.ID_FIELD]))
            else:
                id_field = slugify(self.cleaned_data[self.ID_FIELD])
                
            self.initial.create('%s%s' % (self.PREFIX, id_field))
        else:
            self.initial.save()

        if files:
            for f in files:
                att = files[f]
                self.initial.put_attachment(att, att.name, att.content_type)
                
