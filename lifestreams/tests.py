import doctest
import unittest

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.utils.timezone import now
from django.template import Template, Context

from mock import patch, Mock

from .utils import get_setting, DEFAULT_SETTINGS
from .models import Feed, Lifestream, Item
from .plugins import BasePlugin
from .exceptions import FeedNotConfiguredException, FeedErrorException


class UtilsTest(TestCase):
    def test_get_inexistent_setting(self):
        self.assertIsNone(get_setting('INEXISTENT_SETTING'))
        self.assertEqual('setting', get_setting('INEXISTENT_SETTING', 'setting'))

    def test_get_existent_setting(self):
        self.assertEqual(settings.SITE_ID, get_setting('SITE_ID'))
        self.assertEqual(settings.SITE_ID, get_setting('SITE_ID', 1234124515151))

    def test_get_existent_setting_on_app(self):
        for key in DEFAULT_SETTINGS.keys():
            self.assertEqual(DEFAULT_SETTINGS[key], get_setting(key))


class LifestreamModelTest(TestCase):
    def test_get_items_one_item(self):
        lifestream = Lifestream.objects.create(name='lifestream')
        feed = Feed.objects.create(lifestream=lifestream, title='feed')
        item = Item.objects.create(feed=feed, published=now())
        items = [item]

        result = lifestream.get_items()

        self.assertQuerysetEqual(result, map(repr, items))

    def test_get_items_two_item_two_feed(self):
        lifestream = Lifestream.objects.create(name='lifestream')
        feed1 = Feed.objects.create(lifestream=lifestream, title='feed1')
        Item.objects.create(feed=feed1, published=now())
        feed2 = Feed.objects.create(lifestream=lifestream, title='feed2')
        Item.objects.create(feed=feed2, published=now())
        items = Item.objects.all()

        result = lifestream.get_items()

        self.assertQuerysetEqual(result, map(repr, items))

    def test_get_items_two_item_two_feed_two_lifestreams(self):
        lifestream1 = Lifestream.objects.create(name='lifestream1')
        feed1 = Feed.objects.create(lifestream=lifestream1, title='feed1')
        Item.objects.create(feed=feed1, published=now())
        lifestream2 = Lifestream.objects.create(name='lifestream2')
        feed2 = Feed.objects.create(lifestream=lifestream2, title='feed2')
        Item.objects.create(feed=feed2, published=now())
        items = Item.objects.filter(feed=feed1)

        result = lifestream1.get_items()

        self.assertQuerysetEqual(result, map(repr, items))

    def test_get_items_three_item_three_feed_two_lifestreams(self):
        lifestream1 = Lifestream.objects.create(name='lifestream1')
        feed11 = Feed.objects.create(lifestream=lifestream1, title='feed11')
        Item.objects.create(feed=feed11, published=now())
        feed12 = Feed.objects.create(lifestream=lifestream1, title='feed12')
        Item.objects.create(feed=feed12, published=now())
        lifestream2 = Lifestream.objects.create(name='lifestream2')
        feed2 = Feed.objects.create(lifestream=lifestream2, title='feed2')
        Item.objects.create(feed=feed2, published=now())
        items = Item.objects.filter(feed__lifestream=lifestream1)

        result = lifestream1.get_items()

        self.assertQuerysetEqual(result, map(repr, items))


class LifestreamTagsTest(TestCase):
    def setUp(self):
        lifestream = Lifestream.objects.create(name='lifestream')
        feed = Feed.objects.create(lifestream=lifestream, title='feed', feed_plugin='lifestreams.plugins.BasePlugin')
        self.item = Item.objects.create(feed=feed, published=now())

    def test_load(self):
        template = "{% load lifestream_tags %}"

        Template(template).render(Context())

    @patch('lifestreams.models.Item.render')
    def test_lifestream_render(self, render):
        template = "{% load lifestream_tags %}" \
                   "{% lifestream_render item %}"
        context = Context()
        context.update({'item': self.item})
        expected = unicode(render.return_value)

        result = Template(template).render(context)

        self.assertEqual(expected, result)
        render.assert_called_once_with()

    @patch('lifestreams.models.Item.render')
    def test_lifestream_render_custom_template(self, render):
        template = "{% load lifestream_tags %}" \
                   "{% lifestream_render item template_suffix='suffix/' %}"
        context = Context()
        context.update({'item': self.item})
        expected = unicode(render.return_value)

        result = Template(template).render(context)

        self.assertEqual(expected, result)
        render.assert_called_once_with('suffix/')


class ItemModelTest(TestCase):
    @patch('lifestreams.plugins.BasePlugin')
    @patch('lifestreams.models.Feed.get_plugin')
    @patch('django.template.loader.render_to_string')
    def test_render_without_suffix(self, render_to_string, get_plugin, BasePlugin):
        lifestream = Lifestream.objects.create(name='lifestream')
        feed = Feed.objects.create(lifestream=lifestream, title='feed', feed_plugin='lifestreams.plugins.BasePlugin')
        item = Item.objects.create(feed=feed, published=now())
        plugin = BasePlugin.return_value
        get_plugin.return_value = plugin
        template_name = unicode(plugin.get_template_name.return_value)

        result = item.render()

        self.assertEqual(render_to_string.return_value, result)
        render_to_string.assert_called_once_with(template_name, {'item': item})
        get_plugin.assert_called_once_with()


    @patch('lifestreams.plugins.BasePlugin')
    @patch('lifestreams.models.Feed.get_plugin')
    @patch('django.template.loader.render_to_string')
    def test_render_with_suffix(self, render_to_string, get_plugin, BasePlugin):
        lifestream = Lifestream.objects.create(name='lifestream')
        feed = Feed.objects.create(lifestream=lifestream, title='feed', feed_plugin='lifestreams.plugins.BasePlugin')
        item = Item.objects.create(feed=feed, published=now())
        plugin = BasePlugin.return_value
        get_plugin.return_value = plugin
        suffix = 'suffix/'
        template_name = 'template/template_name.html' 
        plugin.get_template_name.return_value = template_name
        expected_template_name = '%stemplate/template_name.html' % suffix
        
        result = item.render(suffix)

        self.assertEqual(render_to_string.return_value, result)
        render_to_string.assert_called_once_with(expected_template_name, {'item': item})
        get_plugin.assert_called_once_with()


class FeedModelTest(TestCase): 
    def setUp(self):
        self.plugin = 'lifestreams.plugins.BasePlugin'
        lifestream = Lifestream.objects.create(name='dummy')
        self.feed = Feed(title=self.plugin, feed_plugin=self.plugin, lifestream=lifestream)

    def test_get_plugin(self):
        with patch(self.plugin) as MockClass:
            self.assertEqual(MockClass.return_value, self.feed.get_plugin())
            MockClass.assert_called_once_with(feed=self.feed)

    def test_update_feed(self):
        with patch(self.plugin) as MockClass:
            instance = MockClass.return_value
            instance.update.return_value = instance
            return_value = self.feed.update()
            instance.update.assert_called_once_with()
            self.assertEqual(instance, return_value)

    def test_update_feed_not_fetchable(self):
        self.feed.fetchable = False
        self.feed.save()
        with patch(self.plugin) as MockClass:
            instance = MockClass.return_value

            self.feed.update()

            self.assertFalse(instance.update.called)


class BasePluginTest(TestCase):
    def setUp(self):
        lifestream = Lifestream.objects.create(name='dummy')
        self.feed = Feed(title='plugin', feed_plugin='plugin', lifestream=lifestream)

    def test_initialize(self):
        plugin = BasePlugin(feed=self.feed)

        self.assertEqual(self.feed, plugin.feed)

    @patch('lifestreams.plugins.BasePlugin.get_update_kwargs')
    @patch('lifestreams.plugins.BasePlugin.create_item')
    @patch('lifestreams.plugins.BasePlugin.get_handler')
    def test_update_called(self, get_handler, create_item, get_update_kwargs):
        handler = get_handler.return_value
        handler.update.return_value = []
        plugin = BasePlugin(feed=self.feed)

        self.assertEqual(plugin, plugin.update())

    @patch('lifestreams.plugins.BasePlugin.create_item')
    @patch('lifestreams.plugins.BasePlugin.get_handler')
    @patch('lifestreams.plugins.BasePlugin.get_update_kwargs')
    def test_update_called_with_kwargs(self, get_update_kwargs, get_handler, create_item):
        handler = get_handler.return_value
        handler.update.return_value = []
        get_update_kwargs.return_value
        plugin = BasePlugin(feed=self.feed)

        plugin.update()

        get_update_kwargs.assert_called_once_with()
        handler.update.assert_called_once_with(**get_update_kwargs.return_value)

    @patch('lifestreams.plugins.BasePlugin.get_update_kwargs')
    @patch('lifestreams.plugins.BasePlugin.create_item')
    @patch('lifestreams.plugins.BasePlugin.get_handler')
    def test_update_get_handler_called(self, get_handler, create_item, get_update_kwargs):
        handler = get_handler.return_value
        handler.update.return_value = []
        plugin = BasePlugin(feed=self.feed)

        plugin.update()

        get_handler.assert_called_once_with()
        self.assertEqual(handler, plugin.handler)

    @patch('lifestreams.plugins.BasePlugin.get_update_kwargs')
    @patch('lifestreams.plugins.BasePlugin.create_item')
    @patch('lifestreams.plugins.BasePlugin.get_handler')
    def test_update_create_item_called(self, get_handler, create_item, get_update_kwargs):
        handler = get_handler.return_value
        item = Mock()
        handler.update.return_value = [item]
        plugin = BasePlugin(feed=self.feed)

        plugin.update()

        create_item.assert_called_once_with(item)

    def test_not_implemented_get_handler(self):
        plugin = BasePlugin(feed=self.feed)

        self.assertRaises(NotImplementedError, plugin.get_handler)

    def test_not_implemented_create_item(self):
        plugin = BasePlugin(feed=self.feed)

        self.assertRaises(NotImplementedError, plugin.create_item, None)

    def test_not_implemented_get_update_kwargs(self):
        plugin = BasePlugin(feed=self.feed)

        self.assertRaises(NotImplementedError, plugin.get_update_kwargs)

    def test_not_implemented_get_template_name_kwargs(self):
        plugin = BasePlugin(feed=self.feed)

        self.assertRaises(NotImplementedError, plugin.get_template_name)


class UpdateLifestreamsCommandTest(TestCase):
    def setUp(self):
        pass

    @patch('lifestreams.models.Feed.update')
    def test_no_feeds(self, update):
        args = []
        opts = {}
        call_command('update_lifestreams', *args, **opts)

        self.assertFalse(update.called)

    @patch('lifestreams.models.Feed.update')
    def test_one_feed(self, update):
        plugin = 'lifestreams.plugins.BasePlugin'
        lifestream = Lifestream.objects.create(name='dummy')
        feed = Feed(title=plugin, feed_plugin=plugin, lifestream=lifestream)
        feed.save()
        args = []
        opts = {}

        call_command('update_lifestreams', *args, **opts)

        update.assert_called_once_with()

    @patch('lifestreams.models.Feed.update')
    def test_more_feeds(self, update):
        plugin = 'lifestreams.plugins.BasePlugin'
        lifestream = Lifestream.objects.create(name='dummy')
        feed1 = Feed(title=plugin, feed_plugin=plugin, lifestream=lifestream)
        feed2 = Feed(title=plugin, feed_plugin=plugin, lifestream=lifestream)
        feed1.save()
        feed2.save()
        args = []
        opts = {}

        call_command('update_lifestreams', *args, **opts)

        self.assertEqual(Feed.objects.count(), update.call_count)

    @patch('lifestreams.tests.DummyPlugin')
    def test_one_feed_not_configured(self, DummyPlugin):
        lifestream = Lifestream.objects.create(name='dummy')
        DummyPlugin.return_value.update.side_effect = FeedNotConfiguredException
        feed = Feed(title='DummyPlugin', feed_plugin='lifestreams.tests.DummyPlugin', lifestream=lifestream)
        feed.save()
        args = []
        opts = {}

        call_command('update_lifestreams', *args, **opts)

        DummyPlugin.return_value.update.assert_called_once_with()

    @patch('lifestreams.tests.DummyPlugin')
    def test_one_feed_error(self, DummyPlugin):
        lifestream = Lifestream.objects.create(name='dummy')
        DummyPlugin.return_value.update.side_effect = FeedErrorException
        feed = Feed(title='DummyPlugin', feed_plugin='lifestreams.tests.DummyPlugin', lifestream=lifestream)
        feed.save()
        args = []
        opts = {}

        call_command('update_lifestreams', *args, **opts)

        DummyPlugin.return_value.update.assert_called_once_with()

    @patch('lifestreams.plugins.BasePlugin')
    @patch('lifestreams.tests.DummyPlugin')
    def test_two_feeds_one_feed_not_configured(self, DummyPlugin, BasePlugin):
        lifestream = Lifestream.objects.create(name='dummy')
        DummyPlugin.return_value.update.side_effect = FeedNotConfiguredException
        feed1 = Feed(title='DummyPlugin', feed_plugin='lifestreams.tests.DummyPlugin', lifestream=lifestream)
        feed1.save()
        feed2 = Feed(title='BasePlugin', feed_plugin='lifestreams.plugins.BasePlugin', lifestream=lifestream)
        feed2.save()
        args = []
        opts = {}

        call_command('update_lifestreams', *args, **opts)

        DummyPlugin.return_value.update.assert_called_once_with()
        BasePlugin.return_value.update.assert_called_once_with()

    @patch('lifestreams.plugins.BasePlugin')
    @patch('lifestreams.tests.DummyPlugin')
    def test_two_feeds_one_feed_error(self, DummyPlugin, BasePlugin):
        lifestream = Lifestream.objects.create(name='dummy')
        DummyPlugin.return_value.update.side_effect = FeedErrorException
        feed1 = Feed(title='DummyPlugin', feed_plugin='lifestreams.tests.DummyPlugin', lifestream=lifestream)
        feed1.save()
        feed2 = Feed(title='BasePlugin', feed_plugin='lifestreams.plugins.BasePlugin', lifestream=lifestream)
        feed2.save()
        args = []
        opts = {}

        call_command('update_lifestreams', *args, **opts)

        DummyPlugin.return_value.update.assert_called_once_with()
        BasePlugin.return_value.update.assert_called_once_with()

    @patch('lifestreams.plugins.BasePlugin')
    @patch('lifestreams.tests.DummyPlugin')
    def test_two_feeds_two_lifestreams(self, DummyPlugin, BasePlugin):
        lifestream1 = Lifestream.objects.create(name='DummyPlugin')
        lifestream2 = Lifestream.objects.create(name='BasePlugin')
        feed1 = Feed(title='DummyPlugin', feed_plugin='lifestreams.tests.DummyPlugin', lifestream=lifestream1)
        feed1.save()
        feed2 = Feed(title='BasePlugin', feed_plugin='lifestreams.plugins.BasePlugin', lifestream=lifestream2)
        feed2.save()
        args = [lifestream1.name]
        opts = {}

        call_command('update_lifestreams', *args, **opts)

        DummyPlugin.return_value.update.assert_called_once_with()
        self.assertFalse(BasePlugin.called)


class DummyPlugin(BasePlugin):
    pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('lifestreams.utils'))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(UtilsTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(FeedModelTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BasePluginTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(UpdateLifestreamsCommandTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(LifestreamModelTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(LifestreamTagsTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ItemModelTest))
    return suite
