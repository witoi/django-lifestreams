==================
django-lifestreams
==================

.. image:: https://travis-ci.org/witoi/django-lifestreams.png
   :target: https://travis-ci.org/witoi/django-lifestreams
   :alt: Build status

.. image:: https://coveralls.io/repos/witoi/django-lifestreams/badge.png?branch=master
   :target: https://coveralls.io/r/witoi/django-lifestreams?branch=master
   :alt: Coverage Status

**django-lifestreams** is a lifestream application for django. Based on django-lifestream, it allows
you to create a lifestream on your site from any source you want.

A lifestream is compound of feeds, a feed has a source and from that source the application fetch the items.


Plugins
==============

Add plugins to INSTALLED_APPS, and LIFESTREAMS_PLUGIN_CHOICES

Included plugins
----------------

- *Twitter*: `lifestreams.plugins.lifestream_twitter` 
    * Must install tweepy>=2.1
- *Instagram*: `lifestreams.plugins.instagram`
    * Must install python-instagram>=0.8.0
- *RSS*: `lifestreams.plugins.rss`
    * Must install feedparser>=5.0 & python-dateutil>=2.1
  
LIFESTREAMS_PLUGIN_CHOICES example
----------------------------------

::

    LIFESTREAMS_PLUGIN_CHOICES = (
        ('lifestreams.plugins.lifestream_twitter.plugin.TwitterPlugin', 'Twitter'),
        ('lifestreams.plugins.lifestream_instagram.plugin.InstagramPlugin', 'Instagram'),
        ('lifestreams.plugins.lifestream_rss.plugin.RSSPlugin', 'RSS'),
    )                  


Management Command
==================

::

    python manage.py update_lifestreams <lifestream_name>


.. comment: split here