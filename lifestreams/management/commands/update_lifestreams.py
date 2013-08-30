import logging

from django.core.management.base import BaseCommand

from lifestreams.models import Feed
from lifestreams.exceptions import FeedNotConfiguredException, FeedErrorException

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        queryset = self.__get_queryset(args)
        for feed in queryset:
            self.__update(feed)

    def __get_queryset(self, args):
        queryset = Feed.objects.all()
        if args:
            lifestream = ' '.join(args)
            queryset = queryset.filter(lifestream__name=lifestream)
        return queryset

    def __update(self, feed):
        try:
            feed.update()
            logger.info('Feed %s<%d> updated.', feed, feed.id)
        except FeedNotConfiguredException:
            logger.warn('Feed %s<%d> not updated due to FeedNotConfiguredException.', feed, feed.id)
        except FeedErrorException:
            logger.warn('Feed %s<%d> not updated due to a feed error.', feed, feed.id)
