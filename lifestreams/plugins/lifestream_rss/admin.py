from django.contrib import admin

from .models import RSSFeed


class RSSFeedModelAdmin(admin.ModelAdmin):
    pass

admin.site.register(RSSFeed, RSSFeedModelAdmin)
