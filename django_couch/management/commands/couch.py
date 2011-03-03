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
        make_option('--force', '-f', action = 'store_true', dest = 'real_run', default = False, help = u'Real run (change target data)'),
        make_option('--server', '-s', action = 'store', dest = 'server', default = 'http://localhost:5984', help = u'Server address'),
        make_option('--database', '-d', action = 'store', dest = 'database', help = u'Database name'),
        make_option('--path', '-p', action = 'store', dest = 'path', help = u'Working directory', default = '.'),
        make_option('--name', '-n', action = 'store', dest = 'dbkey', help = u'Database key (from settings.py). Will override --server and --database arguments', default = None),
        
    )

    help = u'Backup and restore couchdb database. Usage: ./manage.py couch [restore|backup]'

    extensions = {
        'javascript' : 'js',
        'python' : 'py'
    }
    
    extension2lang = dict(zip(extensions.values(), extensions.keys()))
    
    
    def execute(self, command = None, **options):
        if not command:
            print "No action specified"
            return
        
        if not command in ['restore', 'backup']:
            print "Unknown command:", command
            return
        
        if not options.get('database') and not options.get('dbkey'):
            print "No database specified"
            return

        if options.get('dbkey'):
            db = django_couch.db(options['dbkey'])
        else:
            server = Server(options.get('server'))
            db = server[options.get('database')]
        
        if command == 'backup':
            print "Backing up remote to", options.get('path')
            self.backup(db, options.get('path'))
        elif command == 'restore':
            print "Restoring local path to remote server", options.get('path')
            self.restore(db, options.get('path'), options.get('real_run'), int(options['verbosity']) > 1)
        
        
    def backup(self, db, path):
        
        backup_path = join(path, '_backup', datetime.today().strftime('%Y-%m-%d_%H-%M-%S'))
        
        os.makedirs(backup_path)
        
        for item in django_couch.design_docs(db):
            # document subname
            name = os.path.basename(item.id)
            extension = self.extensions[item.doc.get('language', 'javascript')]
            
            if 'views' in item.doc:
                for view_name in item.doc['views']:
                    dirname = join(backup_path, '%s.%s' % (name, extension), 'views', view_name)
                    os.makedirs(dirname)
                    for view_type in item.doc['views'][view_name]:
                        filename = join(dirname, '%s.%s' % (view_type, extension))
                        print "  Storing %s %s" % (view_type, filename)
                        f = file(filename, 'w')
                        f.write(item.doc['views'][view_name][view_type])
                        f.close()
                        
            if 'filters' in item.doc:
                dirname = join(backup_path, '%s.%s' % (name, extension), 'filters')
                os.makedirs(dirname)
                for filter_name in item.doc['filters']:
                    filename = join(dirname, '%s.%s' % (filter_name, extension))
                    print "  Storing filter %s" % (filename)
                    f = file(filename, 'w')
                    f.write(item.doc['filters'][filter_name])
                    f.close()
                    
                
    def restore(self, db, path, real_run, verbose):
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
            print item
            if not '.' in item:
                if verbose:
                    print "Ignoring", item
                continue
            
            doc_name, extension = item.split('.', 1)
            if extension not in self.extension2lang:
                if verbose:
                    print "Ignoring", item
                continue
            
            language = self.extension2lang[extension]
            
            doc_id = '_design/%s' % doc_name
            changed = False
            try:
                doc = db[doc_id]
                if verbose:
                    print "Design-document %s exists" % doc_id
            except ResourceNotFound:
                if verbose:
                    print "Design-document %s not exists. Creating new" % doc_id
                doc = Document({
                    '_id': doc_id,
                    'language': language,
                    }, _db = db)
                
            
            for key in os.listdir(join(path, item)):
                if key == 'views':
                    for view_name in os.listdir(join(path, item, key)):
                        print "  %s (views)" % view_name
                        map_filename = join(path, item, key, view_name, 'map.%s' % extension)
                        reduce_filename = join(path, item, key, view_name, 'reduce.%s' % extension)
                        map_func = None
                        reduce_func = None
                        
                        if os.path.exists(map_filename):
                            map_func = file(map_filename, 'r').read()
                            
                        if os.path.exists(reduce_filename):
                            reduce_func = file(reduce_filename, 'r').read()
                        
                        if map_func:
                            if not 'views' in doc:
                                doc['views'] = {}

                            if not view_name in doc['views']:
                                doc['views'][view_name] = {}
                            
                            if map_func != doc['views'][view_name].get('map'):
                                doc['views'][view_name]['map'] = map_func
                                changed = True
                                if verbose:
                                    print "    map changed. Updating"
                            else:
                                if verbose:
                                    print "    map not changed"
                                    
                            if reduce_func and reduce_func != doc['views'][view_name].get('reduce'):
                                doc['views'][view_name]['reduce'] = reduce_func
                                changed = True
                                if verbose:
                                    print "    reduce changed. Updating"
                            else:
                                if verbose:
                                    print "    reduce not changed"
                    
                if key in ['filters', 'shows']:
                    for func_filename in os.listdir(join(path, item, key)):
                        if not func_filename.endswith('.' + extension):
                            continue
                        func_name = os.path.splitext(func_filename)[0]
                        print '  %s (%s)' % (func_name, key)
                        if not key in doc:
                            doc[key] = {}
                            
                        filter_func = file(join(path, item, key, func_filename), 'r').read()

                        if filter_func != doc[key].get(func_name):
                            doc[key][func_name] = filter_func
                            changed = True
                            if verbose:
                                print "      differs. Updating"
                        else:
                            if verbose:
                                print "      same"
                            
                        
            if changed:
                print "Changed. Saving..."
                doc.save()
                
                            
                        

        return 
            ## for view in os.listdir(join(path, item)):
            ##     if view == '.svn':
            ##         continue
                
                
            ##     for fun_f in os.listdir(join(path, item, view)):
            ##         if fun_f in ['map.js', 'reduce.js', 'map.py', 'reduce.py']:
                        
            ##             fun, ext = os.path.splitext(fun_f)
                        
            ##             #print "     ", fun
                        
            ##             if ext == '.js':
            ##                 language = 'javascript'
            ##             elif ext == '.py':
            ##                 language = 'python'
                            
            ##             try:
            ##                 d = db['_design/%s' % item]
            ##             except ResourceNotFound:
            ##                 print "Creating design document %s" % item
            ##                 d = Document(_id = '_design/%s' % item,
            ##                              language = language,
            ##                              views = {})
            ##             if not view in d['views']:
            ##                 d['views'][view] = {}
                        
                        
            ##             fun_new = file(join(path, item, view, fun_f), 'r').read()

            ##             if ext in macros:
            ##                  fun_new = fun_new % macros[ext]

            ##             if not fun in d['views'][view] or fun_new != d['views'][view][fun]:
            ##                 print "      Updating view (%s/%s[%s])" % (item, view, fun)
            ##                 d['views'][view][fun] = fun_new
            ##                 if real_run:
            ##                     db[d.id] = d
            ##                 else:
            ##                     print "Fake run, will not change anything"






        

