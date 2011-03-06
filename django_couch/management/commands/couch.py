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
        make_option('--delete', '-r', action = 'store_true', dest = 'delete', help = u'Delete exceed items from database during restore', default = False),
        
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
            self.restore(db, options.get('path'), options)
        
        
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
                    
                
    def restore(self, db, path, options):
        
        real_run = options.get('real_run')
        verbose = int(options.get('verbosity')) > 1
        
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
        
        
        if options['delete']:
            print "Checking for exceed views/filters/shows in design documents"
            delete_docs = []
            for row in django_couch.design_docs(db):
                doc_changed = False
                doc_deleted = False
                
                doc = db[row.id]
                print os.path.basename(doc.id)
                extension = self.extensions[doc.get('language', 'javascript')]
                doc_name = '%s.%s' % (os.path.basename(doc.id), extension)
                
                if os.path.exists(join(path, doc_name)):
                    if 'views' in doc:
                        view_path = join(path, doc_name, 'views')
                        if verbose:
                            print '  checking path', view_path
                        
                        if os.path.exists(view_path):
                            for fun_name in doc['views'].keys(): # copy keys for processing, allow to delete them from loop
                                if verbose:
                                    print '    checking function', fun_name
                        
                                if not os.path.exists(join(view_path, fun_name)):
                                    del(doc['views'][fun_name])
                                    if verbose:
                                        print '      function does not exists. Deleting'
                                    doc_changed = True
                                    
                            pass
                        else:
                            changed = True
                            del(doc['views'])
                            if verbose:
                                print "  Deleting unexistent views entry"
                    for key in ['filters', 'shows']:
                        if key in doc:
                            key_path = join(path, doc_name, key)
                            if verbose:
                                print '  checking path', key_path

                            if os.path.exists(key_path):
                                for fun_name in doc[key].keys():
                                    if verbose:
                                        print '    checking function', fun_name
                                    if not os.path.exists(join(key_path, '%s.%s' % (fun_name, extension))):
                                        del(doc[key][fun_name])
                                        if verbose:
                                            print '    function does not exists. Deleting'
                                        doc_changed = True
                            else:
                                doc_changed = True
                                del(doc[key])
                                if verbose:
                                    print "  Deleting unexistent %s entry" % key

                else:
                    if verbose:
                        print "  Deleting whole document"
                    doc_deleted = True
                    delete_docs.append(row.id)
                
                if not doc_deleted and doc_changed:
                    if real_run:
                        doc.save()
                    else:
                        if verbose:
                            print "Fake run. Skipping doc save"
                
            for doc_id in delete_docs:
                if real_run:
                    doc = db[doc_id]
                    doc.delete()
                else:
                    if verbose:
                        print "Fake run. Skipping doc deleting"

                


        updated = 0
        created = 0
        skipped = 0

        for item in os.listdir(path):
            if not '.' in item:
                if verbose:
                    print "Ignoring", item
                continue
            
            doc_name, extension = item.split('.', 1)
            if extension not in self.extension2lang:
                if verbose:
                    print "Ignoring", item
                continue
            
            print item
            
            language = self.extension2lang[extension]
            
            doc_id = '_design/%s' % doc_name
            changed = False
            
            try:
                doc = db[doc_id]
                creating = False
                if verbose:
                    print "Design-document %s exists" % doc_id
            except ResourceNotFound:
                creating = True
                if verbose:
                    print "Design-document %s not exists. Creating new" % doc_id
                doc = Document({
                    '_id': doc_id,
                    'language': language,
                    }, _db = db)
                
            
            for key in os.listdir(join(path, item)):
                if key == 'views':
                    for view_name in os.listdir(join(path, item, key)):
                        
                        if view_name.startswith('.'):
                            if verbose:
                                print "Skipping hidden file %s" % view_name
                            continue
                        
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
                        if func_filename.startswith('.'):
                            if verbose:
                                print "Skipping hidden file %s" % func_filename
                            continue
                        
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
                if creating:
                    created += 1
                else:
                    updated += 1
                    
                if real_run:
                    print "Changed. Saving..."
                    doc.save()
                else:
                    print "Fake run. Skipping changes"
            else:
                skipped += 1

        if not real_run:
            print "Fake run done"
        print "%d created, %d updated, %d skipped" % (created, updated, skipped)
                        



        

