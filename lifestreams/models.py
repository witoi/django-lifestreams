from django.db import models
from django.utils.translation import ugettext_lazy as _

from .utils import get_setting, split_class_name, get_class


class Lifestream(models.Model):
    '''
    '''
    name = models.CharField(_('Name'), max_length=100)

    class Meta:
        verbose_name = _('Lifestream')
        verbose_name_plural = _('Lifestreams')


class Feed(models.Model):
    '''
    '''
    lifestream = models.ForeignKey('Lifestream', verbose_name=_('Lifestream'), related_name='feeds')
    title = models.CharField(_('Title'), max_length=100)
    feed_plugin = models.CharField(_('Feed Plugin'), max_length=100, choices=get_setting('LIFESTREAMS_FEED_PLUGINS'))
    ordering = models.IntegerField(_('Ordering'), default=0)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)

    class Meta:
        verbose_name = _('Feed')
        verbose_name_plural = _('Feeds')
        ordering = ('ordering', 'created')

    def get_plugin(self):
        plugin_mod_name, plugin_class_name = split_class_name(self.feed_plugin)
        PluginClass = get_class(plugin_mod_name, plugin_class_name)
        return PluginClass(feed=self)

    def update(self):
        plugin = self.get_plugin()
        return plugin.update()


class Item(models.Model):
    '''
    '''
    feed = models.ForeignKey('Feed', verbose_name=_('Feed'), related_name='items')
    content = models.TextField(_('Content'))
    author = models.CharField(_('Author'), max_length=100)
    published = models.DateTimeField(_('Published'))
