from django import forms

class UserForm(forms.Form):
    _type = 'user'
    
    username = forms.CharField(max_length = 64)
    password = forms.CharField(max_length = 128)
    is_staff = forms.BooleanField(required = False)
    
    def save(self):
        print 'saving...', self.cleaned_data
        print 'initial:', self.initial
        self.initial.update(self.cleaned_data)
        self.initial.save()

    
