import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import pytz
import tweepy

from lifestreams.plugins import BasePlugin
from lifestreams.utils import get_setting
from lifestreams.exceptions import FeedNotConfiguredException, FeedErrorException

from .models import ItemTweet, TwitterFeed

__all__ = ['TwitterPlugin', 'TweetsHandler']

logger = logging.getLogger(__name__)

APP_NAME = __name__[0:__name__.rfind('.')]

if APP_NAME not in settings.INSTALLED_APPS:  # pragma: no cover
    raise ImproperlyConfigured(
        "For Lifestreams Twitter plugin you must append %s to INSTALLED_APPS" % APP_NAME)


class TweetsHandler(object):

    def __init__(self, access_token, access_token_secret, screen_name):
        consumer_key = get_setting('TWITTER_CONSUMER_KEY')
        consumer_secret = get_setting('TWITTER_CONSUMER_SECRET')
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.screen_name = screen_name

    def update(self, *args, **kwargs):
        try:
            kwargs.update({'screen_name': self.screen_name})
            return self.api.user_timeline(*args, **kwargs)
        except tweepy.TweepError, e:
            logger.warn('TweepError, %s', e.reason)
            raise FeedErrorException()


class TwitterPlugin(BasePlugin):

    def create_item(self, tweet):
        link = 'https://twitter.com/%s/status/%s' % (
            tweet.author.screen_name, tweet.id)
        item = self.feed.items.create(content=tweet.text,
                                      author=tweet.author.screen_name,
                                      published=pytz.UTC.localize(
                                          tweet.created_at),
                                      link=link)
        itemtweet = ItemTweet(item=item, tweet_id=tweet.id)
        itemtweet.save()

    def get_handler(self):
        return TweetsHandler(**self.get_handler_kwargs())

    def get_handler_kwargs(self):
        try:
            return {
                'access_token': self.feed.twitter.access_token,
                'access_token_secret': self.feed.twitter.access_token_secret,
                'screen_name': self.feed.twitter.screen_name
            }
        except TwitterFeed.DoesNotExist:
            raise FeedNotConfiguredException(
                'Feed must create TwitterFeed for this plugin.')

    def get_update_kwargs(self):
        kwargs = {}
        last_id = self.get_last_id()
        if last_id:
            kwargs['since_id'] = last_id
        return kwargs

    def get_last_id(self):
        try:
            last_item = self.feed.items.latest('published')
            return last_item.tweet.tweet_id
        except self.feed.items.model.DoesNotExist:
            pass

    def get_template_name(self):
        return 'lifestreams/twitter/item.html'
