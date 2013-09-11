from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^social/', include('social_auth.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='auth_login'),
)

urlpatterns += patterns('example.views',
    url(r'^$', 'home', name='home'),
    url(r'^lifestream/$', 'create_lifestream', name='create_lifestream'),
    url(r'^twitter/$', 'create_feed_twitter', name='create_feed_twitter'),
    url(r'^instagram/$', 'create_feed_instagram', name='create_feed_instagram'),
)
