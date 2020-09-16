from django.conf.urls import url
from django.contrib import admin

from .views import ( 
    ProfileUpdateRetrieveDeleteAPIView,
    ProfileUpdateRetrieveStatusAPIView,
    ProfileUpdatePhotoAPIView 
    )

urlpatterns = [ 

    url(r'^$', ProfileUpdateRetrieveDeleteAPIView.as_view(), name='put_profile'), # put (delete) // self update-delete
    url(r'^photo/$', ProfileUpdatePhotoAPIView.as_view(), name='put_photo'), # put
    url(r'^status/$', ProfileUpdateRetrieveStatusAPIView.as_view(), name='put_status'), # put
    url(r'^status/(?P<userId>\d+)/$', ProfileUpdateRetrieveStatusAPIView.as_view(), name='get_status'), # get
    url(r'^(?P<userId>\d+)/$', ProfileUpdateRetrieveDeleteAPIView.as_view(), name='get_profile'), # get 
   ]
