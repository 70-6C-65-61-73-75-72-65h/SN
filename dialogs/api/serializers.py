# from django.shortcuts import get_object_or_404

from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    CharField
    # CurrentUserDefault
    )

from dialogs.models import Conversation, Dialog, DialogForSNUser, ConversationForSNUser
#MyDialogMessage, MyConversationMessage, DialogMessage, ConversationMessage


# from snusers.models import SNUser


# chat_detail_url = HyperlinkedIdentityField(
#         view_name='chats:detail',
#         lookup_field='id'
#         )

# class ListMessageSerializer(ModelSerializer):
#     class Meta:
#         model = Message
#         fields = [
#             'id',
#             'body',
#             'sended',
#             'edited',
#             'author'
#         ]


from dialogs.models import File

class FileSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"




class ListDialogFSNSerializer(ModelSerializer):
    class Meta:
        model = DialogForSNUser
        fields = [
            'id',
            'name',
            'chatTimeStamp',
            'chatTypeId',
        ]

class ListConversationFSNSerializer(ModelSerializer):
    class Meta:
        model = ConversationForSNUser
        fields = [
            'id',
            'name',
            'chatTimeStamp',
            'chatTypeId', 
        ]

class DialogFSNSerializer(ModelSerializer): 
    class Meta:
        model = DialogForSNUser
        fields = [
            'firstNewMsgID',
            'readFromIndex',
            'readFromIndexBefore',
            'chatPhoto',
            'lastMessage',
            'getCountOfNewGlobalMsgs', 
            'members', 
            'name' 
        ]

class ConversationFSNSerializer(ModelSerializer):
    class Meta:
        model = ConversationForSNUser
        fields = [ 
            'firstNewMsgID',
            'readFromIndex',
            'readFromIndexBefore',
            'chatPhoto',
            'lastMessage',
            'getCountOfNewGlobalMsgs', 
            'members', 
            'isAdmin',
            'name'
        ]


class UpdateDFSNNameSerializer(ModelSerializer):
    class Meta:
        model = DialogForSNUser
        fields = ['name']

class UpdateCFSNNameSerializer(ModelSerializer):
    class Meta:
        model = ConversationForSNUser
        fields = ['name']
