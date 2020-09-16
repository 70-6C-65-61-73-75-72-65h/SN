from django.conf.urls import url
from django.contrib import admin

from .views import (
    SNUserListAPIView,
    SNUserDetailAPIView
    )

urlpatterns = [
    url(r'^$', SNUserListAPIView.as_view(), name='list'),
    url(r'^(?P<userId>\d+)/$', SNUserDetailAPIView.as_view(), name='detail'),
]
