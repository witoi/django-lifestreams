==================
django-lifestreams
==================

**django-lifestreams** is a lifestream application for django. Based on django-lifestream, it allows
you to create a lifestream on your site from any source you want.

A lifestream is compound of feeds, a feed has a source and from that source the application fetch the items.


Plugins
==============

Add plugins to INSTALLED_APPS, and LIFESTREAMS_PLUGIN_CHOICES

Included plugins
----------------

- *Twitter*: `lifestreams.plugins.lifestream_twitter`
- *Instagram*: `lifestreams.plugins.instagram`
  
LIFESTREAMS_PLUGIN_CHOICES example
----------------------------------

::

    LIFESTREAMS_PLUGIN_CHOICES = (
        ('lifestreams.plugins.lifestream_twitter.plugin.TwitterPlugin', 'Twitter'),
        ('lifestreams.plugins.lifestream_instagram.plugin.InstagramPlugin', 'Instagram'),
    )                  


Management Command
==================

::

    python manage.py update_lifestreams <lifestream_name>
