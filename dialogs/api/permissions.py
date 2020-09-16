from rest_framework.permissions import BasePermission, SAFE_METHODS
from dialogs.models import DialogForSNUser, ConversationForSNUser
from snusers.models import SNUser
from django.http import Http404
from sn.mixin_functions import responseDecorator

class IsOwnerOrReadOnly(BasePermission):
    message = 'You must be the owner of this object.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwnerOfChatFSN(BasePermission):

    message = 'You must be the owner of this local chat.'

    def get_dial(self, chatId):
        try:
            return DialogForSNUser.objects.get(id=chatId)
        except DialogForSNUser.DoesNotExist:
            return False

    def get_conv(self, chatId):
        try:
            return ConversationForSNUser.objects.get(id=chatId)
        except ConversationForSNUser.DoesNotExist:
            return False

    def getChatObj(self, chatTypeId, chatId):
        if(chatTypeId == "0"):
            return self.get_dial(chatId)
        elif(chatTypeId == "1"):
            return self.get_conv(chatId)
        else:
            raise KeyError(f'chatTypeId should be 1 or 0 not {chatTypeId}')

    # @responseDecorator
    def has_permission(self, request, view):
        # if no chatTypeId and chatId - just get list of them ( and cant do it to other users local chats so its ok)
        if view.kwargs.get('chatTypeId') is None and view.kwargs.get('chatId') is None:
            self.message = "there is no such kwargs"
            return True # for not detailized impact there is no permission to be an object owner
        elif view.kwargs.get('chatTypeId') is not None and view.kwargs.get('chatId') is not None:
            chatTypeId = view.kwargs.get('chatTypeId')
            chatId = view.kwargs.get('chatId')
            chat = self.getChatObj(chatTypeId, chatId)


            if chat == False: # if no such obj in database -> false
                self.message = "such chat doesnt exist"
                return False
            return chat.snuser.userId == request.user.id
        elif view.kwargs.get('chatTypeId') is not None and view.kwargs.get('chatId') is None: # if has one param but hasnt another
            self.message = "there is not enough kwargs to reach chat (missed chatId)"
            return False
        elif view.kwargs.get('chatTypeId') is None and view.kwargs.get('chatId') is not None: # if has one param but hasnt another
            self.message = "there is not enough kwargs to reach chat (missed chatTypeId)"
            return False
        else:
            self.message = 'Wierd Error'
            return False