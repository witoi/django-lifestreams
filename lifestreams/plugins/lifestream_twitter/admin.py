from django.contrib import admin

from .models import TwitterFeed, ItemTweet


class TwitterFeedModelAdmin(admin.ModelAdmin):
    pass


class ItemTweetModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(TwitterFeed, TwitterFeedModelAdmin)
admin.site.register(ItemTweet, ItemTweetModelAdmin)
