from django.conf.urls import url
from django.contrib import admin

from .views import ( 
    CURDChatAPIView,
    ChatListAPIView, 
    MessageListAndCRUDAPIView,
 
    )

 
urlpatterns = [
    url(r'^$', ChatListAPIView.as_view(), name='list'), # just get list
    url(r'^create/$', CURDChatAPIView.as_view(), name='chat-create'), # post chat (create)
    url(r'^(?P<chatTypeId>\d+)/(?P<chatId>\d+)/$', CURDChatAPIView.as_view(), name='chat-detail'), # get delete put ( mult versions of put data)
    url(r'^(?P<chatTypeId>\d+)/(?P<chatId>\d+)/messages/$', MessageListAndCRUDAPIView.as_view(), name='messages-list'), # get messages-list
    url(r'^(?P<chatTypeId>\d+)/(?P<chatId>\d+)/messages/create/$', MessageListAndCRUDAPIView.as_view(), name='message-create'), # post message (create)
    url(r'^(?P<chatTypeId>\d+)/(?P<chatId>\d+)/messages/(?P<messageId>\d+)/$', MessageListAndCRUDAPIView.as_view(), name='messages-item'), # put-delete message
 
] 