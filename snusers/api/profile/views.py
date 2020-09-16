from django.db.models import Q
from django.contrib.auth import get_user_model

from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import Http404

from rest_framework.filters import (
        SearchFilter,
        OrderingFilter,
    )
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView, 
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView
    )



from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,

    )

from snusers.models import SNUser

from snusers.api.pagination import SNUserLimitOffsetPagination, SNUserPageNumberPagination
from snusers.api.permissions import IsOwnerOrReadOnly

from .serializers import (
    ProfileSerializer, #ProfileSerializer0,
    ProfilePhotoSerializer,
    ProfileStatusSerializer
    )

from sn.mixin_functions import responseDecorator



User = get_user_model()

class ProfileUpdateRetrieveDeleteAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = ProfileSerializer

    def get_object(self, userId): # pk may be self (2) ( but userId from AUTH.USER_MODEL) (122) ( if i create users more ( like admins) than snusers )
        try:
            return SNUser.objects.get(userId=userId)
        except SNUser.DoesNotExist:
            raise AttributeError('such snuser doesnt exist')
    
    # /profile/(?P<userId>[\d]+)/$  return just data
    @responseDecorator
    def get(self, request, userId, format=None): 
        profile = self.get_object(userId) # we can just send userId ( and dont give a fuck about our userId it or not)
        serializer = self.serializer_class(profile, context={'request': self.request})
        status = HTTP_201_CREATED
        return (serializer.data, status)

    # /profile/$ PUT
    @responseDecorator
    def put(self, request, format=None): # cant put followed 
        profile = self.get_object(request.user.id)
        # print(request.data)
        serializer = self.serializer_class(profile, data=request.data, context={'request': self.request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data

    # /profile/$ DELETE (nothing returned)
    @responseDecorator
    def delete(self, request, format=None):
        profile = self.get_object(request.user.id) 
        profile.delete()
        request.user.delete()
        status = HTTP_204_NO_CONTENT
        data = None
        return (data, status) 


class ProfileUpdateRetrieveStatusAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = ProfileStatusSerializer
    def get_object(self, userId): # pk may be self (2) ( but userId from AUTH.USER_MODEL) (122) ( if i create users more ( like admins) than snusers )
        try:
            return SNUser.objects.get(userId=userId)
        except SNUser.DoesNotExist:
            raise AttributeError('such snuser doesnt exist')
     
    @responseDecorator
    def get(self, request, userId, format=None):
        profile = self.get_object(userId)
        serializer = self.serializer_class(profile)
        return serializer.data

    # /profile/status/$ PUT
    @responseDecorator
    def put(self, request, format=None): 
        profile = self.get_object(request.user.id)
        # print(profile)
        serializer = self.serializer_class(profile, data=request.data)
        # print(serializer)
        if serializer.is_valid(raise_exception=True):
            serializer.save() 
        return serializer.data



class ProfileUpdatePhotoAPIView(APIView):
    # /profile/status/$ PUT

    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = ProfilePhotoSerializer

    def get_object(self, userId): # pk may be self (2) ( but userId from AUTH.USER_MODEL) (122) ( if i create users more ( like admins) than snusers )
        try:
            return SNUser.objects.get(userId=userId)
        except SNUser.DoesNotExist:
            raise AttributeError('such snuser doesnt exist')
        
    @responseDecorator
    def put(self, request, format=None):
        profile = self.get_object(request.user.id)
        serializer = self.serializer_class(profile, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save() 
        return serializer.data


 











