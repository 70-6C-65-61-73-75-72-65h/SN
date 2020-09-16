from django.conf.urls import url
from django.contrib import admin

from rest_framework_jwt.views import obtain_jwt_token 

from .views import (
    UserCreateAPIView,
    UserLoginAPIView,
    UserIsLoginAPIView 
    )

urlpatterns = [ 
    url(r'^token/$', obtain_jwt_token), # post ( need body (AUTH) to get token) (retrieve user and create token) ( send data )
    url(r'^me/$', UserIsLoginAPIView.as_view(), name='me'), # get ( send token )
    url(r'^login/$', UserLoginAPIView.as_view(), name='login'), # post (retrieve user)  ( send data )
    # url(r'^logout/$', UserLogoutAPIView.as_view(), name='logout'), # post ( send token ) ( resend data to see that it was loggout )
    url(r'^register/$', UserCreateAPIView.as_view(), name='register'), # post ( send data )
]
