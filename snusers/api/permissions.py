from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.http import Http404
from sn.mixin_functions import responseDecorator 


class IsOwnerOrReadOnly(BasePermission):
    message = 'You must be the owner of this object.'


    def get_object(self, userId):
        try:
            return SNUser.objects.get(userId=userId)
        except SNUser.DoesNotExist:
            return False

    # @responseDecorator
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            if(not request.user.is_authenticated):
                self.message = "Unauthorized user trying to edit users info ( may self may other user)" # he can update only self data ( cause there is no change to put over some kwarg userId)
                return False
            else: 
                return True 