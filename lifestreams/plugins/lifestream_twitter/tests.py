"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from mock import patch

from lifestreams.models import Feed, Lifestream

from .plugin import TwitterPlugin

class PluginTest(TestCase):
    def setUp(self):
        self.plugin = 'lifestreams.plugins.lifestream_twitter.plugin.TwitterPlugin'
        lifestream = Lifestream.objects.create(name='dummy')
        self.feed = Feed(title=self.plugin, feed_plugin=self.plugin, lifestream=lifestream)

    def test_called(self):
        consumer_key, consumer_secret, access_token, access_token_secret = [None] * 4
        with patch('lifestreams.plugins.lifestream_twitter.plugin.TweetsHandler') as TweetsHandler:
            TwitterPlugin(feed=self.feed)
            TweetsHandler.assert_called_once_with(consumer_key, consumer_secret, access_token, access_token_secret)
