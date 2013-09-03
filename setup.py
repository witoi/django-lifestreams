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

long_description = read_file('README.rst').strip().split('split here', 1)[0]

setup (
    name='django-lifestreams',
    version=__import__('lifestreams').__version__,
    description=' '.join(__import__('lifestreams').__doc__.splitlines()).strip(),
    long_description=long_description,
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
      'pytz>=2013b'    ],
    tests_require = [
      'mock>=1.0.1',
      'tweepy>=2.1',
      'python-instagram>=0.8.0',
      'feedparser>=5.0',
      'python-dateutil>=2.1'
    ],
    packages=find_packages(),
    test_suite='runtests.runtests',
    zip_safe=True
)
