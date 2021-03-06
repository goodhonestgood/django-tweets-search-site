from django.urls import path
from . import views

app_name = 'tweets'

urlpatterns = [
    path("", views.home, name="home"),
    path("twitterfeed/", views.twitter_feed, name="twitter"),
    path("subscribe/", views.get_twname, name="subscribe"),
]