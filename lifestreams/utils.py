from django.conf import settings

DEFAULT_SETTINGS = {
    'LIFESTREAMS_PLUGIN_CHOICES': (
        ('lifestreams.plugins.lifestream_twitter.plugin.TwitterPlugin', 'Twitter'),
        ('lifestreams.plugins.lifestream_instagram.plugin.InstagramPlugin', 'Instagram'),
        ('lifestreams.plugins.lifestream_rss.plugin.RSSPlugin', 'RSS'),
    )
}


def get_setting(name, default=None):
    if hasattr(settings, name):
        return getattr(settings, name, default)
    return DEFAULT_SETTINGS.get(name, default)


def split_class_name(plugin):
    """
    >>> split_class_name('lifestreams.plugins.twitter.TwitterPlugin')
    ('lifestreams.plugins.twitter', 'TwitterPlugin')
    >>> split_class_name('lifestreams')
    ('lifestreams', '')
    """
    try:
        dot = plugin.rindex('.')
    except ValueError:
        return plugin, ''
    return plugin[:dot], plugin[dot + 1:]


def get_class(module_name, class_name):
    """
    >>> get_class('django.views.generic', 'TemplateView')
    <class 'django.views.generic.base.TemplateView'>
    """
    return getattr(__import__(module_name, {}, {}, ['']), class_name)
