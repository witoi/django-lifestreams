from django.contrib import admin

from .models import InstagramFeed, ItemMedia


class InstagramFeedModelAdmin(admin.ModelAdmin):
    pass


class ItemMediaModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(InstagramFeed, InstagramFeedModelAdmin)
admin.site.register(ItemMedia, ItemMediaModelAdmin)
