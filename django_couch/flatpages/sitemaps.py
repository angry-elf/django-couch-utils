from django.conf import settings
from django.core.urlresolvers import reverse

from datetime import datetime
import django_couch

class FlatPageSitemap:
    changefreq = 'never'
    priority = 0.5
    
    def items(self):
        return django_couch.db().view('pages/attachments').rows
    
    def location(self, obj):
        return obj.key[1]
    
    def lastmod(self, obj):
        d = datetime.strptime(obj.key[0], settings.DATETIME_FMT)
        return d.date()

    def images(self, obj):
        return [reverse('attachment', args = [obj.id, name]) for name in obj.value]
        

    def __get(self, name, obj, default=None):
        try:
            attr = getattr(self, name)
        except AttributeError:
            return default
        if callable(attr):
            return attr(obj)
        return attr

    def get_urls(self):
        urls = []
        for item in self.items():
            loc = "%s%s" % (settings.SITE['domain'], self.location(item))
            url_info = {
                'location':   loc,
                'lastmod':    self.__get('lastmod', item, None),
                'changefreq': self.__get('changefreq', item, None),
                'priority':   self.__get('priority', item, None),
                'images':     ['%s%s' % (settings.SITE['domain'], image_url) for image_url in self.images(item)],
            }
            urls.append(url_info)
        return urls


