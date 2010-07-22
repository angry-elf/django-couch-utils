from forms import UserForm

doc_types = [
    {
        'name': 'User',
        'type': 'user',
        'db': None, # means default
        'view': 'users/list',
        'form': UserForm,
    },
]
