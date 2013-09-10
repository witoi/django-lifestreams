from django.test import TestCase
from django.utils.timezone import now

from mock import patch, Mock
import dateutil.parser

from lifestreams.models import Lifestream, Feed, Item
from lifestreams.exceptions import FeedNotConfiguredException, FeedErrorException

from .models import RSSFeed

from .plugin import RSSPlugin, RSSHandler


class PluginTest(TestCase):
    def setUp(self):
        feed_plugin = 'lifestreams.plugins.lifestream_rss.plugin.RSSPlugin'
        lifestream = Lifestream.objects.create(name='lifestream')
        self.feed = Feed(title=feed_plugin, feed_plugin=feed_plugin, lifestream=lifestream)
        self.feed.save()

    @patch('lifestreams.plugins.lifestream_rss.plugin.RSSHandler')
    def test_get_handler_call_handler(self, RSSHandler):
        plugin = RSSPlugin(feed=self.feed)
        rss_feed = RSSFeed(feed=self.feed, url='http://iwanttobehacker.tumblr.com/rss')
        rss_feed.save()

        result = plugin.get_handler()

        self.assertEqual(rss_feed, plugin.rss_feed)
        self.assertEqual(RSSHandler.return_value, result)
        RSSHandler.assert_called_once_with(url=rss_feed.url)

    def test_get_handler_call_handler_without_rss(self):
        plugin = RSSPlugin(feed=self.feed)

        self.assertRaises(FeedNotConfiguredException, plugin.get_handler)

    @patch('lifestreams.plugins.lifestream_rss.plugin.RSSPlugin.get_update_kwargs')
    @patch('lifestreams.plugins.lifestream_rss.plugin.RSSPlugin.get_handler')
    def test_create_item(self, get_handler, get_update_kwargs):
        rss_feed = RSSFeed(feed=self.feed)
        rss_feed.save()
        handler = get_handler.return_value
        entry = Mock()
        entry.published = 'Tue, 12 Jun 2012 10:43:57 -0400'
        entry.link = 'http://uniquisimo.com'
        handler.update.return_value = [entry]
        plugin = RSSPlugin(feed=self.feed)
        plugin.rss_feed = rss_feed

        plugin.update()

        item = Item.objects.get()
        self.assert_compare_entry_item(entry, item, handler.title)

    @patch('lifestreams.plugins.lifestream_rss.plugin.RSSPlugin.get_update_kwargs')
    @patch('lifestreams.plugins.lifestream_rss.plugin.RSSPlugin.get_handler')
    @patch('lifestreams.plugins.lifestream_rss.plugin.RSSPlugin.include_entry')
    def test_create_item_included(self, include_entry, get_handler, get_update_kwargs):
        rss_feed = RSSFeed(feed=self.feed)
        rss_feed.save()
        handler = get_handler.return_value
        entry = Mock()
        entry.published = 'Tue, 12 Jun 2012 10:43:57 -0400'
        entry.link = 'http://uniquisimo.com'
        handler.update.return_value = [entry]
        plugin = RSSPlugin(feed=self.feed)
        plugin.rss_feed = rss_feed
        include_entry.return_value = False

        plugin.update()

        self.assertEqual(0, self.feed.items.count())

    def test_get_update_kwargs_without_items(self):
        plugin = RSSPlugin(feed=self.feed)

        kwargs = plugin.get_update_kwargs()

        self.assertEqual({}, kwargs)

    def test_include_entry_included(self):
        plugin = RSSPlugin(feed=self.feed)
        entry = Mock()
        entry.published =  'Tue, 12 Jun 2012 10:43:57 -0400'
        entry.link = 'http://uniquisimo.com'
        self.feed.items.create(published=now(), link=entry.link)

        result = plugin.include_entry(entry)

        self.assertFalse(result)

    def test_include_entry_more_entries(self):
        plugin = RSSPlugin(feed=self.feed)
        entry = Mock()
        entry.published = 'Tue, 12 Jun 2012 10:43:57 -0400'
        entry.link = 'http://uniquisimo.com'
        self.feed.items.create(published=now(), link='http://witoi.com')

        result = plugin.include_entry(entry)

        self.assertTrue(result)

    def test_include_entry(self):
        plugin = RSSPlugin(feed=self.feed)
        entry = Mock()
        entry.link = 'http://uniquisimo.com'
        entry.published = 'Tue, 12 Jun 2012 10:43:57 -0400'

        result = plugin.include_entry(entry)

        self.assertTrue(result)

    def assert_compare_entry_item(self, entry, item, title):
        self.assertEqual(unicode(entry.summary), item.content)
        self.assertEqual(unicode(title), item.author)
        published = dateutil.parser.parse(entry.published)
        self.assertEqual(published, item.published)
        self.assertEqual(unicode(entry.link), item.link)

    def test_get_template_name(self):
        feed = Mock()
        plugin = RSSPlugin(feed=feed)

        result = plugin.get_template_name()

        self.assertEqual('lifestreams/rss/item.html', result)

class RSSHandlerTest(TestCase):
    def setUp(self):
        self.url = 'http://uniquisimo.com'

    @patch('feedparser.parse')
    def test_initialize(self, parse):
        handler = RSSHandler(url=self.url)

        self.assertEqual(self.url, handler.url)
        self.assertFalse(parse.called)

    @patch('feedparser.parse')
    @patch('lifestreams.plugins.lifestream_rss.plugin.RSSHandler.get_title')
    def test_update(self, get_title, parse):
        handler = RSSHandler(url=self.url)
        data = parse.return_value
        data.entries = [Mock(), Mock()]

        result = handler.update()

        parse.assert_called_once_with(self.url)
        get_title.assert__called_once_with()
        self.assertEqual(data.entries, result)
        self.assertEqual(get_title.return_value, handler.title)

    @patch('feedparser.parse')
    def test_get_title(self, parse):
        handler = RSSHandler(url=self.url)
        handler.data = Mock()

        result = handler.get_title(handler.data)

        self.assertEqual(handler.data.feed.title, result)

    @patch('feedparser.parse')
    @patch('lifestreams.plugins.lifestream_rss.plugin.RSSHandler.get_title')
    def test_update_no_title(self, get_title, parse):
        handler = RSSHandler(url=self.url)
        data = parse.return_value
        data.entries = [Mock(), Mock()]
        get_title.side_effect = AttributeError

        self.assertRaises(FeedErrorException, handler.update)
