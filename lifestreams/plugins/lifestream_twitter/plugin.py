from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from lifestreams.utils import get_setting
from lifestreams.plugins import BasePlugin

import tweepy

__all__ = ['TwitterPlugin']


APP_NAME = __name__[0:__name__.rfind('.')]

if APP_NAME not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("For Lifestreams Twitter plugin you must append %s to INSTALLED_APPS" % APP_NAME)


TWITTER_ACCESS_TOKEN = get_setting('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = get_setting('TWITTER_ACCESS_TOKEN_SECRET')
TWITTER_CONSUMER_KEY = get_setting('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = get_setting('TWITTER_CONSUMER_SECRET')


class TweetsHandler(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)


class TwitterPlugin(BasePlugin):
    def __init__(self, feed):
        super(TwitterPlugin, self).__init__(feed)
        self.handler = TweetsHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

    def update(self):
        return self
