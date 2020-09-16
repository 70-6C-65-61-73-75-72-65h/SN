"""sn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# mysite/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url 

from django.conf.urls.static import static
from django.conf import settings

from snusers.api.users.views import SNUserFollowAPIView
from dialogs.api.views import UploadDownloadFile

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/users/', include(("snusers.api.users.urls", 'snusers'), namespace='snusers-api')), 
    url(r'^api/profile/', include(("snusers.api.profile.urls", 'profile'), namespace='profile-api')),
    url(r'^api/follow/(?P<userId>\d+)/$', SNUserFollowAPIView.as_view(), name='follow'), # 
    url(r'^api/auth/', include(("accounts.api.urls", 'accounts'), namespace='users-api')), #
    url(r'^api/chats/', include(("dialogs.api.urls", 'dialogs'), namespace='chats')), #
    url(r'^api/files/$',  UploadDownloadFile.as_view(), name='file-upload'), # create ( upload ) # post
    url(r'^api/files/(?P<fileId>\d+)/$',  UploadDownloadFile.as_view(), name='file-download'), # download (?P<chatTypeId>\d+)/(?P<chatId>\d+) # get
 ] 
 