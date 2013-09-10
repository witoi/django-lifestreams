import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import pytz
from instagram import client, InstagramAPIError, InstagramClientError

from lifestreams.plugins import BasePlugin
from lifestreams.exceptions import FeedNotConfiguredException, FeedErrorException

from .models import InstagramFeed, ItemMedia

__all__ = ['InstagramPlugin', 'InstagramHandler']

logger = logging.getLogger(__name__)

APP_NAME = __name__[0:__name__.rfind('.')]

if APP_NAME not in settings.INSTALLED_APPS:  # pragma: no cover
    raise ImproperlyConfigured(
        "For Lifestreams Instagram plugin you must append %s to INSTALLED_APPS" % APP_NAME)


class InstagramHandler(object):

    def __init__(self, access_token):
        self.api = client.InstagramAPI(access_token=access_token)

    def update(self, **kwargs):
        try:
            media, next = self.api.user_recent_media(**kwargs)
            return media
        except InstagramAPIError, e:
            logger.warn(
                "InstagramAPIError, %s-%s", e.error_type, e.error_message)
            raise FeedErrorException()
        except InstagramClientError, e:
            logger.warn("InstagramClientError, %s", e.error_message)
            raise FeedErrorException()


class InstagramPlugin(BasePlugin):

    '''
    '''

    def get_handler(self):
        try:
            instagram = self.feed.instagram
            return InstagramHandler(access_token=instagram.access_token)
        except InstagramFeed.DoesNotExist:
            raise FeedNotConfiguredException

    def create_item(self, media):
        item = self.feed.items.create(
            published=pytz.UTC.localize(media.created_time),
            content=media.get_standard_resolution_url(
            ),
            author=media.user.username,
            link=media.link)
        caption = media.caption and media.caption.text or ''
        ItemMedia.objects.create(
            item=item, instagram_id=media.id, caption=caption)

    def get_update_kwargs(self):
        try:
            item = self.feed.items.latest('published')
        except self.feed.items.model.DoesNotExist:
            return {}
        return {'min_id': item.instagram.instagram_id}

    def get_template_name(self):
        return 'lifestreams/instagram/item.html'