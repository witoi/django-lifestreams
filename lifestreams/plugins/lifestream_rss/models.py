from django.db import models
from django.utils.translation import ugettext_lazy as _


class RSSFeed(models.Model):
    feed = models.OneToOneField('lifestreams.Feed', related_name='rss', verbose_name=_('Feed'))
    url = models.URLField(_('URL'))

    def __unicode__(self):
        return unicode(self.feed)
