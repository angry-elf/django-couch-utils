#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.conf import settings

import django_couch
#from optparse import make_option


class Command(BaseCommand):

    help = u'Requests all couchdb views. Usage: ./manage.py couch_ping <db>, where <db> is couchdb definition from settings.py'

    def execute(self, db_key, **options):
        verbosity = int(options.get('verbosity'))
        if verbosity >= 2:
            print "Using database", db_key
            print "Settings data:", settings.COUCHDB[db_key]
            
        db = django_couch.db(db_key)
        
        for row in django_couch.design_docs(db):
            nop, view = row.id.split('/', 1)
            
            d = db[row.id]
            
            for function in d['views']:
                
                if verbosity >= 2:
                    print 'quering view %s/%s' % (view, function)
                db.view('%s/%s' % (view, function), limit = 1)
                

            



        

