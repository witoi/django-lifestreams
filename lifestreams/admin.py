from django.contrib import admin

from .models import Lifestream, Feed, Item


class LifestreamModelAdmin(admin.ModelAdmin):
    pass


class FeedModelAdmin(admin.ModelAdmin):
    pass


class ItemModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(Lifestream, LifestreamModelAdmin)
admin.site.register(Feed, FeedModelAdmin)
admin.site.register(Item, ItemModelAdmin)
