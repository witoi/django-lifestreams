from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import pytz
import tweepy

from lifestreams.plugins import BasePlugin
from lifestreams.exceptions import FeedNotConfiguredException

from .models import ItemTweet, TwitterFeed

__all__ = ['TwitterPlugin', 'TweetsHandler']


APP_NAME = __name__[0:__name__.rfind('.')]

if APP_NAME not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("For Lifestreams Twitter plugin you must append %s to INSTALLED_APPS" % APP_NAME)


class TweetsHandler(object):
    '''
    '''
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, screen_name):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.screen_name = screen_name

    def update(self, *args, **kwargs):
        kwargs.update({'screen_name': self.screen_name})
        return self.api.user_timeline(*args, **kwargs)


class TwitterPlugin(BasePlugin):
    '''
    '''
    def __init__(self, feed):
        super(TwitterPlugin, self).__init__(feed=feed)
        kwargs = self.get_handler_kwargs()
        self.handler = TweetsHandler(**kwargs)

    def create_item(self, tweet):
        link = 'https://twitter.com/%s/status/%s' % (tweet.author.screen_name, tweet.id)
        item = self.feed.items.create(content=tweet.text,
                                      author=tweet.author.screen_name,
                                      published=pytz.UTC.localize(tweet.created_at),
                                      link=link)
        itemtweet = ItemTweet(item=item, tweet_id=tweet.id)
        itemtweet.save()

    def get_handler(self):
        return self.handler

    def get_handler_kwargs(self):
        try:
            return {
                'consumer_key': self.feed.twitter.consumer_key,
                'consumer_secret': self.feed.twitter.consumer_secret,
                'access_token': self.feed.twitter.access_token,
                'access_token_secret': self.feed.twitter.access_token_secret,
                'screen_name': self.feed.twitter.screen_name
            }
        except TwitterFeed.DoesNotExist:
            raise FeedNotConfiguredException('Feed must create TwitterFeed for this plugin.')

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
