import doctest
import unittest

from django.test import TestCase
from django.conf import settings

from mock import patch

from .utils import get_setting, DEFAULT_SETTINGS
from .models import Feed, Lifestream


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

def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('lifestreams.utils'))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(UtilsTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(FeedModelTest))
    return suite