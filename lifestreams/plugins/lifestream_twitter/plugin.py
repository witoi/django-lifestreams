from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import tweepy

from lifestreams.utils import get_setting
from lifestreams.plugins import BasePlugin
from lifestreams.exceptions import FeedNotConfiguredException

from .models import ItemTweet, TwitterFeed

__all__ = ['TwitterPlugin', 'TweetsHandler']


APP_NAME = __name__[0:__name__.rfind('.')]

if APP_NAME not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("For Lifestreams Twitter plugin you must append %s to INSTALLED_APPS" % APP_NAME)


class TweetsHandler(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, screen_name):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.screen_name = screen_name

    def update(self, *args, **kwargs):
        kwargs.update({'screen_name': self.screen_name})
        return self.api.user_timeline(*args, **kwargs)


class TwitterPlugin(BasePlugin):
    def __init__(self, feed):
        super(TwitterPlugin, self).__init__(feed=feed)
        consumer_key = get_setting('TWITTER_CONSUMER_KEY')
        consumer_secret = get_setting('TWITTER_CONSUMER_SECRET')
        access_token = get_setting('TWITTER_ACCESS_TOKEN')
        access_token_secret = get_setting('TWITTER_ACCESS_TOKEN_SECRET')
        screen_name = self.get_screen_name()
        self.handler = TweetsHandler(consumer_key=consumer_key,
                                     consumer_secret=consumer_secret,
                                     access_token=access_token,
                                     access_token_secret=access_token_secret,
                                     screen_name=screen_name)

    def update(self):
        tweets = self.handler.update(**self.get_update_kwargs())
        for tweet in tweets:
            self.create_item(tweet)
        return self

    def create_item(self, tweet):
        item = self.feed.items.create(content=tweet.text,
                                      author=tweet.author.screen_name,
                                      published=tweet.created_at)
        itemtweet = ItemTweet(item=item, tweet_id=tweet.id)
        itemtweet.save()

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

    def get_screen_name(self):
        try:
            return self.feed.twitter.screen_name
        except TwitterFeed.DoesNotExist:
            raise FeedNotConfiguredException('Feed must create TwitterFeed for this plugin.')
