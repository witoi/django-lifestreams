from django.db import models
from django.utils.translation import ugettext_lazy as _


class ItemTweet(models.Model):
	item = models.OneToOneField('lifestreams.Item', related_name='tweet', verbose_name=_('Item'))

	tweet_id = models.CharField(max_length=100)
