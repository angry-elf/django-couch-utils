#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

from os.path import join

from couchdb import Server, Document, ResourceNotFound
import simplejson
import urllib
import getopt
from datetime import datetime


def usage():
    print """Usage: ./do.py [-k] [-s <http://server:5984/>] [-d <database>] [-p path] command
    -k - fake run (no data will be real pushed)
    -s - server (default: http://localhost:5984)
    -d - database (default: phones)
    -p - path (default: .)
    command - one of:
        push: push directory to server
        pull: pull server to directory
        backup: backup server to directory/_backup
        
"""

try:
    optlist, args = getopt.getopt(sys.argv[1:], 's:hd:p:k')
except getopt.GetoptError, error:
    print "Error:", error
    usage()
    sys.exit(1)

server = 'http://localhost:5984/'
database = 'phones'

path = '.'
fake_run = False
print "Loading settings"
for o, a in optlist:
    if o == '-h':
        usage()
        sys.exit(0)
    if o == '-s':
        server = a
        print "  Server:", server
    if o == '-p':
        path = a
        print "  Path:", path
    if o == '-d':
        database = a
        print "  Database:", database
    if o == '-k':
        fake_run = True
        print "  Fake run"
        
if server[-1] != '/':
    server += '/'
    
try:
    command = args[0]
    assert command in ['push', 'pull', 'backup']
except:
    usage()
    sys.exit(1)
    
print "Action:", command
print
print "Connecting to", server

s = Server(server)
print "Using DB", database
db = s[database]

def backup(db, server, path):

    u = urllib.urlopen('%s%s/_all_docs?limit=40&startkey="_design"&endkey="_design0"' % (server.resource.uri, db.name))
    
    design_docs = [i['key'] for i in simplejson.loads(u.read())['rows']]
    b_path = join(path, '_backup', datetime.today().strftime('%Y-%m-%d_%H-%M-%S'))
    
    os.makedirs(b_path)
    
    for id in design_docs:
        document = db[id]
        name = os.path.basename(id)
        for view_name in document['views']:
            #print join(b_path, name, view_name)
            os.makedirs(join(b_path, name, view_name))
            for view_type in document['views'][view_name]:
                print "  Storing file", join(b_path, name, view_name, '%s.js' % view_type)
                f = file(join(b_path, name, view_name, '%s.js' % view_type), 'w')
                f.write(document['views'][view_name][view_type])
                f.close()
                

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

if command == 'backup':
    print "Backing up"
    backup(db, s, path)
    
elif command == 'push':
    macros = macros_load(path)

    for item in os.listdir(path):
        if item in ['.svn', '_backup', '_macros'] or not os.path.isdir(join(path, item)):
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



                
                
                
