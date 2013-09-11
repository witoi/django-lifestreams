from django.views.generic import TemplateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings

import tweepy

from lifestreams.models import Lifestream, Item
from lifestreams.plugins.lifestream_twitter.models import TwitterFeed
from lifestreams.plugins.lifestream_instagram.models import InstagramFeed


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self):
        context = super(HomeView, self).get_context_data()
        context['items'] = Item.objects
        return context

home = HomeView.as_view()


class CreateLifestreamView(DetailView):
    template_name = 'create_lifestream.html'

    @method_decorator(login_required)
    def dispatch(self, request):
        return super(CreateLifestreamView, self).dispatch(request=request)

    def get_object(self):
        lifestream, self.created = Lifestream.objects.get_or_create(name=self.request.user.username)
        return lifestream

create_lifestream = CreateLifestreamView.as_view()


class CreateFeedTwitterView(DetailView):
    template_name = 'create_feed_twitter.html'

    @method_decorator(login_required)
    def dispatch(self, request):
        self.lifestream = get_object_or_404(Lifestream, name=self.request.user.username)
        return super(CreateFeedTwitterView, self).dispatch(request=request)

    def get_object(self):
        feed, self.created = self.lifestream.feeds.get_or_create(title='twitter',
                                                                 feed_plugin='lifestreams.plugins.lifestream_twitter.plugin.TwitterPlugin')
        if self.created:
            self.create_twitter_feed(feed=feed)
        return feed

    def create_twitter_feed(self, feed):
        social_auth = self.request.user.social_auth.filter(provider='twitter').latest('pk')
        access_token = social_auth.tokens['oauth_token']
        access_token_secret = social_auth.tokens['oauth_token_secret']
        consumer_key = settings.TWITTER_CONSUMER_KEY
        consumer_secret = settings.TWITTER_CONSUMER_SECRET
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        screen_name = self.get_screen_name(auth)
        TwitterFeed.objects.create(screen_name=screen_name, feed=feed, access_token=access_token, access_token_secret=access_token_secret)

    def get_screen_name(self, auth):
        api = tweepy.API(auth)
        return api.me().screen_name

create_feed_twitter = CreateFeedTwitterView.as_view()


class CreateFeedInstagramView(DetailView):
    template_name = 'create_feed_instagram.html'

    @method_decorator(login_required)
    def dispatch(self, request):
        self.lifestream = get_object_or_404(Lifestream, name=self.request.user.username)
        return super(CreateFeedInstagramView, self).dispatch(request=request)

    def get_object(self):
        feed, self.created = self.lifestream.feeds.get_or_create(title='instagram',
                                                                 feed_plugin='lifestreams.plugins.lifestream_instagram.plugin.InstagramPlugin')
        if self.created:
            self.create_instagram_feed(feed=feed)
        return feed

    def create_instagram_feed(self, feed):
        social_auth = self.request.user.social_auth.filter(provider='instagram').latest('pk')
        InstagramFeed.objects.create(feed=feed, access_token=social_auth.extra_data['access_token'])

create_feed_instagram = CreateFeedInstagramView.as_view()
