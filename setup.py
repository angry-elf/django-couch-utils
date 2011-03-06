#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='django-couch-utils',
      version='1.1.1',
      description='Handy tools and helpers for django projects, powered by CouchDB',
      author='Alexey Loshkarev',
      author_email='elf2001@gmail.com',
      url='https://github.com/angry-elf/django-couch-utils/',
      packages=find_packages(),
      #package_data={'django_couch.admin': 'templates'},
      license='GPL',
      classifiers=[
          "Development Status :: 5 - Production/Stable", 
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      install_requires = ['couchdb-python-curl'],
      package_data = {'django_couch.admin': ['templates/admin/*.html'] },
      include_package_data = True,
      #data_files = ['admin/templates/admin/base.html']
      )
