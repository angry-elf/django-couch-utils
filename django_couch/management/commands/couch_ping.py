#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from django.core.management.base import BaseCommand
from django.conf import settings

import django_couch
#from optparse import make_option

import multiprocessing

class Pinger(multiprocessing.Process):
    def __init__(self, verbosity, db_key, view_name, func_name):
        multiprocessing.Process.__init__(self)

        self.verbosity = verbosity
        self.db_key = db_key
        self.view_name = view_name
        self.func_name = func_name
        
    def run(self):
        db = django_couch.db(self.db_key)
        if self.verbosity >= 2:
            print 'quering view %s/%s' % (self.view_name, self.func_name)
        db.view('%s/%s' % (self.view_name, self.func_name), limit = 0).rows
                

class Command(BaseCommand):

    help = u'Requests all couchdb views. Usage: ./manage.py couch_ping <db>, where <db> is couchdb definition from settings.py'

    def execute(self, *args, **options):
        
        verbosity = int(options.get('verbosity'))
        
        workers = []

        if not len(args):
            print "No database to ping"
            sys.exit(1)
            
        for db_key in args:
            if verbosity >= 2:
                print "Using database", db_key
                print "Settings data:", settings.COUCHDB[db_key]

            db = django_couch.db(db_key)

            for row in django_couch.design_docs(db):
                nop, view = row.id.split('/', 1)

                d = db[row.id]

                for function in d.get('views', []):
                    worker = Pinger(verbosity, db_key, view, function)
                    workers.append(worker)
                    worker.start()

        for worker in workers:
            if verbosity > 1:
                print "Waiting for worker %s (%s/%s @ %s)..." % (worker, worker.view_name, worker.func_name, worker.db_key)
            worker.join()
            if verbosity > 1:
                print '  done'
        
        
        
            



        

