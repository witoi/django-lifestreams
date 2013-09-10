from django.db import models
from django.utils.translation import ugettext_lazy as _

from .utils import get_setting, split_class_name, get_class


class Lifestream(models.Model):
    '''
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)

    def get_items(self):
        return Item.objects.filter(feed__lifestream=self)

    class Meta:
        verbose_name = _('Lifestream')
        verbose_name_plural = _('Lifestreams')

    def __unicode__(self):
        return self.name



class Feed(models.Model):
    '''
    '''
    lifestream = models.ForeignKey('Lifestream', verbose_name=_('Lifestream'), related_name='feeds')
    title = models.CharField(_('Title'), max_length=100)
    feed_plugin = models.CharField(_('Feed Plugin'), max_length=100, choices=get_setting('LIFESTREAMS_PLUGIN_CHOICES'))
    ordering = models.IntegerField(_('Ordering'), default=0)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    fetchable = models.BooleanField(_('Fetchable'), default=True)

    class Meta:
        verbose_name = _('Feed')
        verbose_name_plural = _('Feeds')
        ordering = ('ordering', 'created')

    def get_plugin(self):
        plugin_mod_name, plugin_class_name = split_class_name(self.feed_plugin)
        PluginClass = get_class(plugin_mod_name, plugin_class_name)
        return PluginClass(feed=self)

    def update(self):
        if self.fetchable:
            plugin = self.get_plugin()
            return plugin.update()

    def __unicode__(self):
        return "%s - %s" % (self.lifestream.name, self.title)


class Item(models.Model):
    '''
    '''
    feed = models.ForeignKey('Feed', verbose_name=_('Feed'), related_name='items')
    content = models.TextField(_('Content'))
    author = models.CharField(_('Author'), max_length=100)
    link = models.URLField(_('Link'))
    published = models.DateTimeField(_('Published'))

    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)

    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
        ordering = ('-published', '-created', '-updated')


    def __unicode__(self):
        return "%s %s" % (self.author, self.published)

    def render(self, suffix=''):
        from django.template.loader import render_to_string
        plugin = self.feed.get_plugin()
        default_template_name = plugin.get_template_name()
        template_name = '%s%s' % (suffix, default_template_name)
        return render_to_string(template_name, {'item': self})
