from datetime import datetime

from django.test import TestCase
from django.test.utils import override_settings
from django.utils.timezone import is_aware

import pytz
from mock import patch, Mock
from tweepy import TweepError

from lifestreams.models import Feed, Lifestream
from lifestreams.exceptions import FeedNotConfiguredException, FeedErrorException

from .plugin import TwitterPlugin, TweetsHandler
from .models import TwitterFeed



class PluginTest(TestCase):
    def setUp(self):
        self.access_token = 'c'
        self.access_token_secret = 'd'
        self.plugin = 'lifestreams.plugins.lifestream_twitter.plugin.TwitterPlugin'
        self.lifestream = Lifestream.objects.create(name='dummy')
        self.feed = Feed(title=self.plugin, feed_plugin=self.plugin, lifestream=self.lifestream)
        self.feed.save()
        self.twitter_feed = TwitterFeed(feed=self.feed,
                                        screen_name='uniquisimo',
                                        access_token=self.access_token,
                                        access_token_secret=self.access_token_secret)
        self.twitter_feed.save()
    
    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    def test_handler_called(self, TweetsHandler):
        handler = TweetsHandler.return_value
        plugin = TwitterPlugin(feed=self.feed)

        self.assertEqual(handler, plugin.get_handler())
        TweetsHandler.assert_called_once_with(access_token=self.access_token,
                                              access_token_secret=self.access_token_secret,
                                              screen_name=self.twitter_feed.screen_name)

    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    @patch('lifestreams.plugins.lifestream_twitter.plugin.TwitterPlugin.__init__')
    def test_get_handler_kwargs_without_twitter_feed(self, init, TweetsHandler):
        init.return_value = None
        feed = Feed(title=self.plugin, feed_plugin=self.plugin, lifestream=self.lifestream)
        feed.save()
        plugin = TwitterPlugin()
        plugin.feed = feed

        self.assertRaises(FeedNotConfiguredException, plugin.get_handler_kwargs)

    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    def test_access_from_twitter_feed(self, TweetsHandler):
        consumer_key, consumer_secret, access_token, access_token_secret = ['d', 'c', 'b', 'a']
        screen_name = 'pedro_witoi'
        feed = Feed(title=self.plugin, feed_plugin=self.plugin, lifestream=self.lifestream)
        feed.save()
        twitter_feed = TwitterFeed(feed=feed, screen_name=screen_name,
                                   access_token=access_token,
                                   access_token_secret=access_token_secret)
        twitter_feed.save()
        plugin = TwitterPlugin(feed=feed)

        plugin.get_handler()
        
        TweetsHandler.assert_called_once_with(access_token=access_token,
                                              access_token_secret=access_token_secret,
                                              screen_name=screen_name)

    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    @patch('lifestreams.plugins.lifestream_twitter.plugin.TwitterPlugin.get_handler_kwargs')
    def test_get_handler_kwargs_called(self, get_handler_kwargs, TweetsHandler):
        plugin = TwitterPlugin(feed=self.feed)

        plugin.get_handler()
        
        get_handler_kwargs.assert_called_once_with()

    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    def test_update_handler_update(self, TweetsHandler):
        handler = TweetsHandler.return_value
        plugin = TwitterPlugin(feed=self.feed)

        returns = plugin.update()

        self.assertEqual(plugin, returns)
        handler.update.assert_called_once_with()

    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    def test_update_item_created(self, TweetsHandler):
        tweet = Mock()
        tweet.created_at = datetime.now()
        tweets = [tweet]
        handler = TweetsHandler.return_value
        handler.update.return_value = tweets
        plugin = TwitterPlugin(feed=self.feed)

        plugin.update()

        self.assertEqual(1, self.feed.items.count())
        item = self.feed.items.get()
        self.assert_compare_tweet_item(tweet, item)

    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    def test_update_items_created(self, TweetsHandler):
        tweet1 = Mock()
        tweet1.created_at = datetime.now()
        tweet2 = Mock()
        tweet2.created_at = datetime.now()
        tweets = [tweet1, tweet2]
        handler = TweetsHandler.return_value
        handler.update.return_value = tweets
        plugin = TwitterPlugin(feed=self.feed)

        plugin.update()

        self.assertEqual(2, self.feed.items.count())
        item2 = self.feed.items.all()[0]
        item1 = self.feed.items.all()[1]
        self.assert_compare_tweet_item(tweet1, item1)
        self.assert_compare_tweet_item(tweet2, item2)

    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    def test_update_items_created_with_already_created(self, TweetsHandler):
        tweet1 = Mock()
        tweet1.created_at = datetime.now()
        handler = TweetsHandler.return_value
        plugin = TwitterPlugin(feed=self.feed)
        plugin.create_item(tweet1)
        tweet2 = Mock()
        tweet2.created_at = datetime.now()
        handler.update.return_value = [tweet2]

        plugin.update()
        handler.update.assert_called_with(since_id=unicode(tweet1.id))

    def assert_compare_tweet_item(self, tweet, item):
        self.assertEqual(unicode(tweet.text), item.content)
        self.assertEqual(unicode(tweet.author.screen_name), item.author)
        published = pytz.UTC.localize(tweet.created_at)
        self.assertEqual(published, item.published)
        self.assertEqual(unicode(tweet.id), item.tweet.tweet_id)
        link = 'https://twitter.com/%s/status/%s' % (tweet.author.screen_name, tweet.id)
        self.assertEqual(link, item.link)
        self.assertTrue(is_aware(item.published))

    def test_get_template_name(self):
        feed = Mock()
        plugin = TwitterPlugin(feed=feed)

        result = plugin.get_template_name()

        self.assertEqual('lifestreams/twitter/item.html', result)


@override_settings(TWITTER_CONSUMER_KEY='TWITTER_CONSUMER_KEY')
@override_settings(TWITTER_CONSUMER_SECRET='TWITTER_CONSUMER_SECRET')
class TweetsHandlerTest(TestCase):
    def setUp(self):
        self.consumer_key = 'TWITTER_CONSUMER_KEY'
        self.consumer_secret = 'TWITTER_CONSUMER_SECRET'
        self.access_token = 'c'
        self.access_token_secret = 'd'
        self.screen_name = 'pedro_witoi'

    @patch('tweepy.OAuthHandler')
    @patch('tweepy.API')
    def test_intialize(self, API, OAuthHandler):
        auth = OAuthHandler.return_value

        TweetsHandler(access_token=self.access_token, access_token_secret=self.access_token_secret,
                      screen_name=self.screen_name)

        OAuthHandler.assert_called_once_with(self.consumer_key, self.consumer_secret)
        auth.set_access_token.assert_called_once_with(self.access_token, self.access_token_secret)
        API.assert_called_once_with(auth)

    @patch('tweepy.OAuthHandler')
    @patch('tweepy.API')
    @override_settings(TWITTER_CONSUMER_KEY='a')
    @override_settings(TWITTER_CONSUMER_SECRET='b')
    def test_intialize_different_settings(self, API, OAuthHandler):
        auth = OAuthHandler.return_value

        TweetsHandler(access_token=self.access_token, access_token_secret=self.access_token_secret,
                      screen_name=self.screen_name)

        OAuthHandler.assert_called_once_with('a', 'b')
        auth.set_access_token.assert_called_once_with(self.access_token, self.access_token_secret)
        API.assert_called_once_with(auth)

    @patch('tweepy.API')
    def test_update(self, API):
        handler = TweetsHandler(access_token=self.access_token, access_token_secret=self.access_token_secret,
                                screen_name=self.screen_name)
        api = API.return_value

        result = handler.update()

        api.user_timeline.assert_called_once_with(screen_name=self.screen_name)
        self.assertEqual(api.user_timeline.return_value, result)

    @patch('tweepy.API')
    def test_update_since_id(self, API):
        handler = TweetsHandler(access_token=self.access_token, access_token_secret=self.access_token_secret,
                                screen_name=self.screen_name)
        api = API.return_value

        result = handler.update(since_id=1)

        api.user_timeline.assert_called_once_with(screen_name=self.screen_name, since_id=1)
        self.assertEqual(api.user_timeline.return_value, result)

    @patch('tweepy.API')
    def test_update_error(self, API):
        handler = TweetsHandler(access_token=self.access_token, access_token_secret=self.access_token_secret,
                                screen_name=self.screen_name)
        api = API.return_value
        api.user_timeline.side_effect = TweepError('reason')

        self.assertRaises(FeedErrorException, handler.update)

        api.user_timeline.assert_called_once_with(screen_name=self.screen_name)
