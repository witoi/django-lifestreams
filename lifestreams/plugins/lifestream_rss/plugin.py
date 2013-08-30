import time
from datetime import datetime

from lifestreams.plugins import BasePlugin
from lifestreams.exceptions import FeedNotConfiguredException, FeedErrorException

import feedparser

from .models import RSSFeed

__all__ = ['RSSHandler', 'RSSPlugin']


class RSSHandler(object):
    def __init__(self, url):
        self.url = url

    def update(self):
        try:
            data = feedparser.parse(self.url)
            self.title = self.get_title(data)
            return data.entries
        except AttributeError:
            raise FeedErrorException

    def get_title(self, data):
        return data.feed.title


class RSSPlugin(BasePlugin):
    def get_handler(self):
        try:
            self.rss_feed = self.feed.rss
            return RSSHandler(url=self.rss_feed.url)
        except RSSFeed.DoesNotExist:
            raise FeedNotConfiguredException

    def create_item(self, entry):
        if self.include_entry(entry):
            published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            self.feed.items.create(published=published,
                                   content=entry.summary,
                                   author=self.handler.title,
                                   link=entry.link)

    def get_update_kwargs(self):
        return {}

    def include_entry(self, entry):
        return not self.feed.items.filter(link=entry.link).exists()
