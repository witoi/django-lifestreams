#!/usr/bin/env python
import sys
import os

from django.conf import settings


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'lifestreams',
            'lifestreams.plugins.lifestream_twitter',
        ),
        SITE_ID=1,
        SECRET_KEY='this-is-just-for-tests-so-not-that-secret',
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'handlers': {
                'null': {
                    'level': 'DEBUG',
                    'class': 'logging.NullHandler'
                },
                'console':{
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler'
                }
            },
            'loggers': {
                '': {
                    'handlers': [os.getenv('LIFESTREAMS_LOGGER_HANDLER', 'null')],
                    'propagate': True,
                    'level': 'DEBUG',
                }
            }
        }
    )


from django.test.utils import get_runner

def runtests():
    failfast = os.getenv('LIFESTREAMS_FAILFAST', 'False') == 'True'
    interactive = os.getenv('LIFESTREAMS_INTERACTIVE', 'True') == 'True'
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=interactive, failfast=failfast)
    failures = test_runner.run_tests(['lifestreams', 'lifestream_twitter'])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
