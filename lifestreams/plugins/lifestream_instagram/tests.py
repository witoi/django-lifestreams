from datetime import datetime

from django.test import TestCase
from django.utils.timezone import is_aware, now

import pytz
from mock import patch, Mock
from instagram import InstagramAPIError, InstagramClientError

from lifestreams.models import Lifestream, Feed, Item
from lifestreams.exceptions import FeedNotConfiguredException, FeedErrorException

from .plugin import InstagramPlugin, InstagramHandler
from .models import InstagramFeed, ItemMedia


class PluginTest(TestCase):
    def setUp(self):
        feed_plugin = 'lifestreams.plugins.lifestream_instagram.plugin.InstagramPlugin'
        lifestream = Lifestream.objects.create(name='lifestream')
        self.feed = Feed(title=feed_plugin, feed_plugin=feed_plugin, lifestream=lifestream)
        self.feed.save()

    @patch('lifestreams.plugins.lifestream_instagram.plugin.InstagramHandler')
    def test_get_handler_call_handler(self, InstagramHandler):
        access_token = 'access_token'
        instagram_feed = InstagramFeed(feed=self.feed, access_token=access_token)
        instagram_feed.save()
        plugin = InstagramPlugin(feed=self.feed)

        result = plugin.get_handler()

        self.assertEqual(InstagramHandler.return_value, result)
        InstagramHandler.assert_called_once_with(access_token=access_token)

    def test_get_handler_call_handler_without_instagram(self):
        plugin = InstagramPlugin(feed=self.feed)

        self.assertRaises(FeedNotConfiguredException, plugin.get_handler)

    @patch('lifestreams.plugins.lifestream_instagram.plugin.InstagramPlugin.get_update_kwargs')
    @patch('lifestreams.plugins.lifestream_instagram.plugin.InstagramPlugin.get_handler')
    def test_create_item(self, get_handler, get_update_kwargs):
        access_token = 'access_token'
        instagram_feed = InstagramFeed(feed=self.feed, access_token=access_token)
        instagram_feed.save()
        handler = get_handler.return_value
        media = Mock()
        media.created_time = datetime.now()
        handler.update.return_value = [media]
        plugin = InstagramPlugin(feed=self.feed)

        plugin.update()

        item = Item.objects.get()
        self.assert_compare_media_item(media, item)

    @patch('lifestreams.plugins.lifestream_instagram.plugin.InstagramPlugin.get_update_kwargs')
    @patch('lifestreams.plugins.lifestream_instagram.plugin.InstagramPlugin.get_handler')
    def test_create_item_caption_none(self, get_handler, get_update_kwargs):
        access_token = 'access_token'
        instagram_feed = InstagramFeed(feed=self.feed, access_token=access_token)
        instagram_feed.save()
        handler = get_handler.return_value
        media = Mock()
        media.created_time = datetime.now()
        media.caption = None
        handler.update.return_value = [media]
        plugin = InstagramPlugin(feed=self.feed)

        plugin.update()

        item = Item.objects.get()
        self.assert_compare_media_item(media, item)

    def test_get_update_kwargs_without_items(self):
        plugin = InstagramPlugin(feed=self.feed)

        kwargs = plugin.get_update_kwargs()

        self.assertEqual({}, kwargs)

    def test_get_update_kwargs_with_item(self):
        access_token = 'access_token'
        instagram_feed = InstagramFeed(feed=self.feed, access_token=access_token)
        instagram_feed.save()
        item1 = self.feed.items.create(content='a', author='a', published=now())
        ItemMedia.objects.create(item=item1, instagram_id='1')
        item2 = self.feed.items.create(content='b', author='a', published=now())
        ItemMedia.objects.create(item=item2, instagram_id='2')
        plugin = InstagramPlugin(feed=self.feed)

        kwargs = plugin.get_update_kwargs()

        self.assertEqual({'min_id': '2'}, kwargs)

    def assert_compare_media_item(self, media, item):
        self.assertEqual(unicode(media.get_standard_resolution_url.return_value), item.content)
        self.assertEqual(unicode(media.user.username), item.author)
        published = pytz.UTC.localize(media.created_time)
        self.assertEqual(published, item.published)
        self.assertEqual(unicode(media.id), item.instagram.instagram_id)
        caption = media.caption and media.caption.text or ''
        self.assertEqual(unicode(caption), item.instagram.caption)
        self.assertEqual(unicode(media.link), item.link)
        self.assertTrue(is_aware(item.published))

    def test_get_template_name(self):
        feed = Mock()
        plugin = InstagramPlugin(feed=feed)

        result = plugin.get_template_name()

        self.assertEqual('lifestreams/instagram/item.html', result)

class InstagramHandlerTest(TestCase):
    def setUp(self):
        self.access_token = 'a'

    @patch('instagram.client.InstagramAPI')
    def test_initialize(self, InstagramAPI):
        InstagramHandler(access_token=self.access_token)

        InstagramAPI.assert_called_once_with(access_token=self.access_token)

    @patch('instagram.client.InstagramAPI')
    def test_update(self, InstagramAPI):
        handler = InstagramHandler(access_token=self.access_token)
        api = InstagramAPI.return_value
        api.user_recent_media.return_value = (Mock(), Mock())

        result = handler.update()

        api.user_recent_media.assert_called_once_with()
        self.assertEqual(api.user_recent_media.return_value[0], result)

    @patch('instagram.client.InstagramAPI')
    def test_update_since_id(self, InstagramAPI):
        handler = InstagramHandler(access_token=self.access_token)
        api = InstagramAPI.return_value
        api.user_recent_media.return_value = (Mock(), Mock())

        result = handler.update(min_id=1)

        api.user_recent_media.assert_called_once_with(min_id=1)
        self.assertEqual(api.user_recent_media.return_value[0], result)

    @patch('instagram.client.InstagramAPI')
    def test_update_with_api_error(self, InstagramAPI):
        handler = InstagramHandler(access_token=self.access_token)
        api = InstagramAPI.return_value
        api.user_recent_media.return_value = (Mock(), Mock())
        api.user_recent_media.side_effect = InstagramAPIError(400, 'error_type', 'error_message')

        self.assertRaises(FeedErrorException, handler.update)

        api.user_recent_media.assert_called_once_with()

    
    @patch('instagram.client.InstagramAPI')
    def test_update_with_client_error(self, InstagramAPI):
        handler = InstagramHandler(access_token=self.access_token)
        api = InstagramAPI.return_value
        api.user_recent_media.return_value = (Mock(), Mock())
        api.user_recent_media.side_effect = InstagramClientError('client_error_message')

        self.assertRaises(FeedErrorException, handler.update)

        api.user_recent_media.assert_called_once_with()
