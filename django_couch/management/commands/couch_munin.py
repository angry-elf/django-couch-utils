#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import munin

from munin import MuninPlugin


from django.core.management.base import BaseCommand
from django.conf import settings
import django_couch
from time import time

class CouchTypesPlugin(MuninPlugin):
    title = "DocTypes grow stats"
    vlabel = "count"
    category = "couchdb"

    def __init__(self, db, *args, **kwargs):
        MuninPlugin.__init__(self, *args, **kwargs)
        self.db = django_couch.db(db)

    @property
    def fields(self):
        
        return [(row.key, {
            "label": row.key,
            "info": "%s count" % row.key,
            "type": "COUNTER",
            "min": 0,
            
            }) for row in self.db.view('types/list', reduce = True, group = True).rows]

    def execute(self):
        for row in self.db.view('types/list', reduce = True, group = True).rows:
            print "%s.value %s" % (row.key, row.value)
        

class Command(BaseCommand):
    
    def execute(self, db, *args, **options):
        munin = CouchTypesPlugin(db)
        sys.argv = [''] + list(args)
        munin.run()
        
    def usage(self, subcommand):
        return 'aaaaaaaa %s' % subcommand


