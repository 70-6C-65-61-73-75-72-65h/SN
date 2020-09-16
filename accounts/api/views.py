from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.filters import (
        SearchFilter,
        OrderingFilter,
    )

from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView, 
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
    )
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from .serializers import (
    UserCreateSerializer, 
    )


from sn.mixin_functions import responseDecorator
from django.contrib.auth import authenticate


User = get_user_model()

# /auth/register
class UserCreateAPIView(APIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    @responseDecorator
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True): # словлю на уровне выше в декораторе и пропишу эту ошибку
            serializer.save()
        return serializer.data


from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate

# /auth/login
class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    # while we send POST request for login   :/api/auth/login/
    @responseDecorator
    def post(self, request, *args, **kwargs):
        try:
            # print(request.data)
            data = request.data # username + passowrd (TODO make email + password)
            if('username' not in data and 'password' not in data):
                raise KeyError('no username or password provided to token creation while operation LOGIN') 
            user = authenticate(username=data['username'], password=data['password'])
            # print(user)
            if user is None:
                raise ValueError('Wrong auth data')
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return ({ 'token': token,  'userId': user.id,  'email': user.email, 'login': user.username }, HTTP_201_CREATED)
        # except Exception as ex:
        except KeyError:
            return (None, HTTP_400_BAD_REQUEST, { 'errorMessage': 'Invalid user data' })
        except ValueError:
            return (None, HTTP_400_BAD_REQUEST, { 'errorMessage': 'Wrong username or passowrd' })


from django.urls import reverse, reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
 
# /auth/me
class UserIsLoginAPIView(RetrieveAPIView):

    permission_classes = [AllowAny]
    # serializer_class = UserLoginSerializer

    # while we send GET request for check is login  :/api/auth/me/
    @responseDecorator
    def get(self, request, format=None):
        # check on token in request
        print('me')
        print(request.user.is_authenticated)

        userId = userEmail = userLogin = None
        # resultCode = 0
        data = None
        response = None 
        if request.user.is_authenticated: 
            data = {
                'userId': request.user.id,
                'email': request.user.email,
                'login': request.user.username
            }
            response = (data, HTTP_200_OK)
        else:
            response = (data, HTTP_200_OK, {'errorMessage': 'Anonymous User'}) 
        

        return response
 