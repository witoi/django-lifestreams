from django.test import TestCase
from django.test.utils import override_settings
from django.utils.timezone import now

from mock import patch, Mock

from lifestreams.models import Feed, Lifestream

from .plugin import TwitterPlugin, TweetsHandler


@override_settings(TWITTER_CONSUMER_KEY='a', TWITTER_CONSUMER_SECRET='b',
                   TWITTER_ACCESS_TOKEN='c', TWITTER_ACCESS_TOKEN_SECRET='d')
class PluginTest(TestCase):
    def setUp(self):
        self.plugin = 'lifestreams.plugins.lifestream_twitter.plugin.TwitterPlugin'
        lifestream = Lifestream.objects.create(name='dummy')
        self.feed = Feed(title=self.plugin, feed_plugin=self.plugin, lifestream=lifestream)
        self.feed.save()
    
    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    def test_handler_called(self, TweetsHandler):
        consumer_key, consumer_secret, access_token, access_token_secret = ['a', 'b', 'c', 'd']
        
        TwitterPlugin(feed=self.feed)
        
        TweetsHandler.assert_called_once_with(consumer_key, consumer_secret, access_token, access_token_secret)

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
        tweet.created_at = now()
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
        tweet1.created_at = now()
        tweet2 = Mock()
        tweet2.created_at = now()
        tweets = [tweet1, tweet2]
        handler = TweetsHandler.return_value
        handler.update.return_value = tweets
        plugin = TwitterPlugin(feed=self.feed)

        plugin.update()

        self.assertEqual(2, self.feed.items.count())
        item1 = self.feed.items.all()[0]
        item2 = self.feed.items.all()[1]
        self.assert_compare_tweet_item(tweet1, item1)
        self.assert_compare_tweet_item(tweet2, item2)

    @patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler')
    def test_update_items_created_with_already_created(self, TweetsHandler):
        tweet1 = Mock()
        tweet1.created_at = now()
        handler = TweetsHandler.return_value
        plugin = TwitterPlugin(feed=self.feed)
        plugin.create_item(tweet1)
        tweet2 = Mock()
        tweet2.created_at = now()
        handler.update.return_value = [tweet2]

        plugin.update()
        handler.update.assert_called_with(since_id=unicode(tweet1.id))

    def assert_compare_tweet_item(self, tweet, item):
        self.assertEqual(unicode(tweet.text), item.content)
        self.assertEqual(unicode(tweet.author.screen_name), item.author)
        self.assertEqual(tweet.created_at, item.published)
        self.assertEqual(unicode(tweet.id), item.tweet.tweet_id)


class TweetsHandlerTest(TestCase):
    def setUp(self):
        self.consumer_key = 'a'
        self.consumer_secret = 'b'
        self.access_token = 'c'
        self.access_token_secret = 'd'

    @patch('tweepy.OAuthHandler')
    @patch('tweepy.API')
    def test_intialize(self, API, OAuthHandler):
        auth = OAuthHandler.return_value

        TweetsHandler(self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret)

        OAuthHandler.assert_called_once_with(self.consumer_key, self.consumer_secret)
        auth.set_access_token.assert_called_once_with(self.access_token, self.access_token_secret)
        API.assert_called_once_with(auth)

    @patch('tweepy.API')
    def test_update(self, API):
        handler = TweetsHandler(self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret)
        api = API.return_value

        result = handler.update()

        api.user_timeline.assert_called_once_with()
        self.assertEqual(api.user_timeline.return_value, result)

    @patch('tweepy.API')
    def test_update_since_id(self, API):
        handler = TweetsHandler(self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret)
        api = API.return_value

        result = handler.update(since_id=1)

        api.user_timeline.assert_called_once_with(since_id=1)
        self.assertEqual(api.user_timeline.return_value, result)
