#!/usr/bin/env python
import os
from setuptools import setup, find_packages

def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup (
    name='django-lifestreams',
    version='0.1',
    description=' '.join(__import__('lifestreams').__doc__.splitlines()).strip(),
    author='Pedro Buron',
    author_email='pedro@witoi.com',
    url='http://github.com/witoi/django-lifestreams',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Plugins',
      'Framework :: Django',
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires = [
      'Django>=1.4',
    ],
    tests_require = [
      'mock>=1.0.1',
    ],
    packages=find_packages(),
    test_suite='runtests.runtests',
    zip_safe=True
)
