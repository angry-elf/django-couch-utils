#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

from django.core.management.base import BaseCommand


from os.path import join

from couchdbcurl import Server, Document, ResourceNotFound
import django_couch
from optparse import make_option

import urllib
import getopt
from datetime import datetime


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--fake', '-k', action = 'store_true', dest = 'fake_run', default = False, help = u'Fake run (do nothing)'),
        make_option('--server', '-s', action = 'store', dest = 'server', default = 'http://localhost:5984', help = u'Server address'),
        make_option('--database', '-d', action = 'store', dest = 'database', help = u'Database name'),
        make_option('--path', '-p', action = 'store', dest = 'path', help = u'Working directory', default = '.'),
        
    )

    help = u'Backup and restore couchdb database. Usage: ./manage.py couch [restore|backup]'

    extensions = {
        'javascript' : '.js',
        'python' : '.py'
    }
    

    def execute(self, command = None, **options):
        if not command:
            print "No action specified"
            return
        
        if not command in ['restore', 'backup']:
            print "Unknown command:", command
            return
        if not options.get('database'):
            print "No database specified"
            return

        server = Server(options.get('server'))
        db = server[options.get('database')]
            
        if command == 'backup':
            print "Backing up remote to", options.get('path')
            self.backup(db, options.get('path'))
        elif command == 'restore':
            print "Restoring local path to remote server", options.get('path')
            self.restore(db, options.get('path'), options.get('fake_run'))
            
       
    def backup(self, db, path):
        
        backup_path = join(path, '_backup', datetime.today().strftime('%Y-%m-%d_%H-%M-%S'))
        
        os.makedirs(backup_path)
        
        for item in django_couch.design_docs(db):
            name = os.path.basename(item.id)
            
            for view_name in item.doc['views']:
                os.makedirs(join(backup_path, name, view_name))
                for view_type in item.doc['views'][view_name]:
                    print "  Storing file", join(backup_path, name, view_name, '%s%s' % (view_type, self.extensions[item.doc['language']]))
                    f = file(join(backup_path, name, view_name, '%s.js' % view_type), 'w')
                    f.write(item.doc['views'][view_name][view_type])
                    f.close()
 
    def restore(self, db, path, fake_run):

        def macros_load(path):
            macros = {}
            if os.path.exists(join(path, '_macros')):
                for f in os.listdir(join(path, '_macros')):
                    name, ext = os.path.splitext(f)
                    if ext in ['.js', '.py']:
                        if not ext in macros:
                            macros[ext] = {}
                        macros[ext][name] = file(join(path, '_macros', f), 'r').read()

            return macros
        
        macros = macros_load(path)
        
        for item in os.listdir(path):
            if item in ['_backup', '_macros'] or not os.path.isdir(join(path, item)) or item.startswith('.'):
                continue
            #print item
            
            for view in os.listdir(join(path, item)):
                if view == '.svn':
                    continue
                
                
                for fun_f in os.listdir(join(path, item, view)):
                    if fun_f in ['map.js', 'reduce.js', 'map.py', 'reduce.py']:
                        
                        fun, ext = os.path.splitext(fun_f)
                        
                        #print "     ", fun
                        
                        if ext == '.js':
                            language = 'javascript'
                        elif ext == '.py':
                            language = 'python'
                            
                        try:
                            d = db['_design/%s' % item]
                        except ResourceNotFound:
                            print "Creating design document %s" % item
                            d = Document(_id = '_design/%s' % item,
                                         language = language,
                                         views = {})
                        if not view in d['views']:
                            d['views'][view] = {}
                        
                        
                        fun_new = file(join(path, item, view, fun_f), 'r').read()

                        if ext in macros:
                             fun_new = fun_new % macros[ext]

                        if not fun in d['views'][view] or fun_new != d['views'][view][fun]:
                            print "      Updating view (%s/%s[%s])" % (item, view, fun)
                            d['views'][view][fun] = fun_new
                            if not fake_run:
                                db[d.id] = d
                            else:
                                print "Fake run, will not change anything"






        

