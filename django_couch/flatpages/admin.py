from forms import *

doc_types = [
    {
        'name': 'Page',
        'type': 'page',
        'db': None, # means default
        'view': 'pages/list',
        'form': FlatpageForm,
        'attachments': True,
    },

]
