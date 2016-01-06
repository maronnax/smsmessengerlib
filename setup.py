# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='smsmessenger',
    version='0.0.1',
    author='Nathan Addy',
    author_email='nathan.addy@gmail.com',
    packages=['smsmessenger'],
    url='http://bitbucket.org/bruno/django-geoportail',
    license='BSD licence, see LICENCE.txt',
    description='Add maps and photos from the French National Geographic' + \
                ' Institute to GeoDjango',
    long_description=open('README.txt').read(),
    zip_safe=False,
)
