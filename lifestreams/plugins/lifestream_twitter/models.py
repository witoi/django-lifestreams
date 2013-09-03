from django.db import models
from django.utils.translation import ugettext_lazy as _


class TwitterFeed(models.Model):
    feed = models.OneToOneField('lifestreams.Feed', related_name='twitter', verbose_name=_('Feed'))
    screen_name = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100)
    access_token_secret = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.feed)


class ItemTweet(models.Model):
    item = models.OneToOneField('lifestreams.Item', related_name='tweet', verbose_name=_('Item'))

    tweet_id = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.item)
