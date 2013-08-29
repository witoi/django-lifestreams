from django.db import models
from django.utils.translation import ugettext_lazy as _


class InstagramFeed(models.Model):
    feed = models.OneToOneField('lifestreams.Feed', related_name='instagram', verbose_name=_('Feed'))
    access_token = models.CharField(_('Access Token'), max_length=255)

    def __unicode__(self):
        return unicode(self.feed)


class ItemMedia(models.Model):
    item = models.OneToOneField('lifestreams.Item', related_name='instagram', verbose_name=_('Item'))
    instagram_id = models.CharField(_('Instagram ID'), max_length=100)
    caption = models.TextField(_('Caption'))

    def __unicode__(self):
        return unicode(self.item)

    class Meta:
        ordering = ('item',)
