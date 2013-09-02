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
        USE_TZ=True,
        INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'lifestreams',
            'lifestreams.plugins.lifestream_twitter',
            'lifestreams.plugins.lifestream_instagram',
            'lifestreams.plugins.lifestream_rss',
        ),
        SITE_ID=1,
        SECRET_KEY='this-is-just-for-tests-so-not-that-secret',
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'handlers': {
                'console':{
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler'
                }
            },
            'loggers': {
                '.': {
                    'handlers': ['console'],
                    'propagate': True,
                    'level': 'DEBUG',
                }
            }
        }
    )


from django.test.utils import get_runner

def runtests():
    failfast = os.getenv('FAILFAST', 'False') == 'True'
    interactive = os.getenv('INTERACTIVE', 'True') == 'True'
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=interactive, failfast=failfast)
    failures = test_runner.run_tests(['lifestreams', 'lifestream_twitter',
                                      'lifestream_instagram', 'lifestream_rss'])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
