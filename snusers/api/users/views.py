from django.db.models import Q 
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import Http404

from rest_framework.filters import (
        SearchFilter,
        OrderingFilter,
    )

from rest_framework.generics import (
    ListAPIView, 
    RetrieveAPIView
    )

from rest_framework.views import APIView


from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,

    )

from snusers.models import SNUser

from snusers.api.pagination import SNUserLimitOffsetPagination, SNUserPageNumberPagination 

from .serializers import (
    SNUserListDetailSerializer,
    ProfileFollowSerializer
    )

from sn.mixin_functions import responseDecorator

from rest_framework.renderers import JSONRenderer




class SNUserDetailAPIView(RetrieveAPIView):
    queryset = SNUser.objects.all()
    serializer_class = SNUserListDetailSerializer
    lookup_field='userId' 
    permission_classes = [AllowAny] 


# /users
class SNUserListAPIView(ListAPIView):
    serializer_class = SNUserListDetailSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [AllowAny]
    search_fields = ['name']
    pagination_class = SNUserPageNumberPagination #PageNumberPagination
 
    # /users
    def get_queryset(self, *args, **kwargs): 
        queryset_list = SNUser.objects.all() #filter(user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                    Q(name__icontains=query)|
                    Q(status__icontains=query)
                    ).distinct()
        return queryset_list
 
# /follow/{userId}
class SNUserFollowAPIView(APIView):

    serializer_class = ProfileFollowSerializer

    # /follow/{userId}
    def get_object(self, userId):
        try:
            return SNUser.objects.get(userId=userId)
        except SNUser.DoesNotExist:
            raise AttributeError('such snuser doesnt exist')
    
    # Is followed
    @responseDecorator
    def get(self, request, userId, format=None):
        snuser = self.get_object(userId)
        serializer = self.serializer_class(snuser, context={'request': self.request}) # send obj and context
        # status = HTTP_200_OK
        response = {
            'userRelation': serializer.data['userRelation']
        }
        return response

    def post_delete_follow(self, request, function, userId):
        snuser = self.get_object(userId)
        me = self.get_object(request.user.id)
        function = function.__get__(me, me.__class__)(snuser)
        
        serializer = self.serializer_class(snuser, context={'request': self.request}) # get the answer after put
        return serializer.data

    # follow ( по идее должен быть put )
    @responseDecorator
    def post(self, request, userId, format=None): # post without data - NOT COOL!!!
        return (self.post_delete_follow(request, SNUser.addToFollow, userId), HTTP_201_CREATED)

    # unfollow
    @responseDecorator
    def delete(self, request, userId, format=None):
        return(self.post_delete_follow(request, SNUser.removeFromFollow, userId), HTTP_204_NO_CONTENT)
