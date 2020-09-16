from django.db.models import Q
from django.shortcuts import get_object_or_404  
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


from dialogs.models import Conversation, Dialog, DialogForSNUser, ConversationForSNUser, ConversationMessage, File
from snusers.models import SNUser

 
from dialogs.api.permissions import IsOwnerOfChatFSN#, IsOwnerOrReadOnly

from .serializers import (
    ListDialogFSNSerializer,
    ListConversationFSNSerializer,
    DialogFSNSerializer,
    ConversationFSNSerializer,
    UpdateDFSNNameSerializer,
    UpdateCFSNNameSerializer,
    

    FileSerializer 
    )

from sn.mixin_functions import responseDecorator, listsPaginatorP, listsPaginatorM
from rest_framework.renderers import JSONRenderer

from itertools import chain
from rest_framework.parsers import FileUploadParser
 



class UploadDownloadFile(APIView):
    permission_classes = [IsAuthenticated] # IsOwnerOfChatFSN
    parser_class = (FileUploadParser,)

    def get_file(self, fileId): 
        try:
            return File.objects.get(id=int(fileId))
        except File.DoesNotExist:
            raise AttributeError('such File doesnt exist')

 
    def post(self, request,  *args, **kwargs):
        try:
            print('file_serializer')
            fileURL = request.data['fileURL']  
            fileName = request.data['fileName']
 
            _format, _img_str = fileURL.split(';base64,')
            _format = _format.split(':')[1]
 
            isImage = True if _format.split('/')[0] == 'image' else False
            file = File.objects.create(file=fileURL, name=fileName, format=_format, isImage=isImage) # in TextField

            return Response({'data': {'fileId':file.id, 'fileName':file.name, 'isImage': file.isImage}}, status=HTTP_201_CREATED)
        except Exception as ex:
            return Response(ex, status=HTTP_400_BAD_REQUEST)
 

    def get(self, request, fileId,  *args, **kwargs): # , chatTypeId, chatId

        file = self.get_file(fileId)
        file_serializer = FileSerializer(file)
        print(f'donwload file with fileId {fileId}')
 
        if 'id' in file_serializer.data:
            return Response(file_serializer.data, status=HTTP_200_OK)
        else:
            return Response(file_serializer.errors, status=HTTP_400_BAD_REQUEST)
 


class ChatListAPIView(ListAPIView):
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    search_fields = ['name'] 


    def get_user(self, userId):
        try:
            return SNUser.objects.get(userId=userId)
        except SNUser.DoesNotExist:
            raise AttributeError('such snuser doesnt exist')

    @responseDecorator
    def get(self, request, format=None):
        me = self.get_user(request.user.id)
        dialogs = me.getDialogs()
        conversations = me.getConversations()
        
        query = request.GET.get("q")
        if query:
            dialogs = dialogs.filter(
                    Q(name__icontains=query) # name of DFSN or CFSN
                    ).distinct()
            conversations = conversations.filter(
                    Q(name__icontains=query) # name of DFSN or CFSN
                    ).distinct()

        if dialogs != [] and dialogs.count() > 0:
            dialogs = [ListDialogFSNSerializer(dialog).data for dialog in dialogs]
        else:
            dialogs = []
        if conversations != [] and conversations.count() > 0:
            conversations = [ListConversationFSNSerializer(conversation).data for conversation in conversations]
        else:
            conversations = []

        queryset_list = dialogs + conversations
        queryset_list = sorted(queryset_list, key=lambda chat: chat['chatTimeStamp'], reverse=True)
        return listsPaginatorP(request, queryset_list, query, 'chats')




    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)


class MessageListAndCRUDAPIView(APIView):
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated, IsOwnerOfChatFSN]
    search_fields = ['body', 'author__name'] ############

    def get_message(self, chat, messageId):
        try:
            return chat.messages.get(id=messageId)
        except Exception as ex:
            print(ex)
            raise AttributeError('such message doesnt exist')

    def get_dialog(self, chatId):
        try:
            return DialogForSNUser.objects.get(id=chatId)
        except DialogForSNUser.DoesNotExist:
            raise AttributeError('such dialog doesnt exist')
    def get_conversation(self, chatId):
        try:
            return ConversationForSNUser.objects.get(id=chatId)
        except ConversationForSNUser.DoesNotExist:
            raise AttributeError('such conversation doesnt exist')
    def getChatObject(self, chatTypeId, chatId):
        if(chatTypeId == "0"):
            return self.get_dialog(chatId)
        elif(chatTypeId == "1"):
            return self.get_conversation(chatId)
        else:
            raise KeyError(f'chatTypeId should be 1 or 0 not {chatTypeId}')



    @responseDecorator # readFromIndex
    def get(self, request, chatTypeId, chatId, format=None): # REACT.api.ChatsAPI.getMessages()
        """
        Return a list of all users.
        """
        try:
            chat = self.getChatObject(chatTypeId, chatId) # chatObj
            oldLocalMessages, oldGlobalMessages = chat.getOldGlobalMsgs # black color
            newLocalMessages, newGlobalMessages = chat.getNewGlobalMsgs # blue color
            query = self.request.GET.get("q")
            if query:
                oldLocalMessages = [] if isinstance(oldLocalMessages, list) else oldLocalMessages.filter(
                        Q(body__icontains=query) |
                        Q(snuser__snuser__name__icontains=query)
                        ).distinct()
                oldGlobalMessages = [] if isinstance(oldGlobalMessages, list) else oldGlobalMessages.filter(
                        Q(body__icontains=query) |
                        Q(author__name__icontains=query) # author ====  snuser__snuser  (property wont work???) for my messages # for global - author
                        ).distinct()
                newLocalMessages = [] if isinstance(newLocalMessages, list) else newLocalMessages.filter(
                        Q(body__icontains=query) |
                        Q(snuser__snuser__name__icontains=query)
                        ).distinct()
                newGlobalMessages = [] if isinstance(newGlobalMessages, list) else newGlobalMessages.filter(
                        Q(body__icontains=query) |
                        Q(author__name__icontains=query)
                        ).distinct()
            oldMsgs = chat.serializeMsgs(oldLocalMessages, oldGlobalMessages, True)  # make 1 array of old 
            newMsgs = chat.serializeMsgs(newLocalMessages, newGlobalMessages, False)
            unionMsgs = sorted(oldMsgs + newMsgs, key=lambda arr: arr['sended']) # decsending order ( newest - heiger ( but in visual part - it will be lower))
            
            rfib = request.GET.get("readFromIndexBefore") 
            readFromIndexBefore = None if rfib is None or rfib=='null' else int(rfib)# for first time it eqauls None

            possibleFRI = int(request.GET.get("readFromIndex"))  
            possibleFRIN = chat.readFromIndexCalcNext(possibleFRI)


            if len(oldMsgs) == 0:
                return listsPaginatorM(request, unionMsgs, possibleFRI, possibleFRIN, readFromIndexBefore) 
            # нет старых сообщений для допрогрузки
            if possibleFRI == possibleFRIN:
                return listsPaginatorM(request, unionMsgs, possibleFRI, possibleFRIN, readFromIndexBefore) 


            numOfDeletedMsgs = int(request.GET.get("numOfDeletedMsgs"))
            readFromIndex = None

            sortedOM = sorted(oldMsgs, key=lambda arr: arr['id'])
            have_such_RFI_Yet_QUERYSET = False # не удалили ли мы еще это сообщение чтобы с него делать отсчет
            for msg in sortedOM:
                if msg['id'] == possibleFRI: 
                    have_such_RFI_Yet_QUERYSET = True 

            for index, value in enumerate(sortedOM):
                if(have_such_RFI_Yet_QUERYSET):
                    if value['id'] == possibleFRI: 
                        if index - numOfDeletedMsgs > 0: 
                            readFromIndex = sortedOM[index - numOfDeletedMsgs]['id']
                        else: 
                            readFromIndex = sortedOM[0]['id'] 
                else:
                    if value['id'] > possibleFRI: 
                        if index - numOfDeletedMsgs > 0: #  в этом случае точно удалили это сообщение потому numOfDeletedMsgs точно 1+
                            readFromIndex = sortedOM[index  - numOfDeletedMsgs]['id']
                        else:
                            readFromIndex = sortedOM[0]['id'] 
                if readFromIndex != None:
                    break 
            readFromIndexNext = chat.readFromIndexCalcNext(readFromIndex) 
            kkek = listsPaginatorM(request, unionMsgs, readFromIndex, readFromIndexNext, readFromIndexBefore) # чтобы когда мы добовляем сообщения нас не отбрасывало назад из прогруженных
            # print(kkek)
            return kkek
        except Exception as ex:
            print(ex)
            return 'None'




    @responseDecorator
    def post(self, request, chatTypeId, chatId, *args, **kwargs):
        chat = self.getChatObject(chatTypeId, chatId)
        postData = request.data
        print(f'msg creation with postData {postData}')
        if 'messageBody' in postData:
            if 'fileId' in postData:
                chat.createNewMessage(postData['messageBody'], fileId=postData['fileId']) # can be another error if unappropriate type of messageBody
            else:
                chat.createNewMessage(postData['messageBody'])
        else: 
            raise KeyError('there is no key "messageBody" in postData')
        return ({'created': True}, HTTP_201_CREATED)

    @responseDecorator
    def put(self, request, chatTypeId, chatId, messageId, format=None):
        chat = self.getChatObject(chatTypeId, chatId)
        message = self.get_message(chat, messageId)
        putData = request.data
        if 'newMessageBody' in putData:
            chat.editMyMessage(putData['newMessageBody'], message)
        else: 
            raise KeyError('there is no key "newMessageBody" in putData')
        return {'edited': True}

    @responseDecorator
    def delete(self, request, chatTypeId, chatId, messageId, format=None):
        try:
            chat = self.getChatObject(chatTypeId, chatId)
            message = self.get_message(chat, messageId)
            chat.deleteMyMessage(message)
            return (None, HTTP_200_OK)
        except Exception as ex:
            print(ex)
 
 
class CURDChatAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOfChatFSN] 
    def get_user(self, userId): # pk may be self (2) ( but userId from AUTH.USER_MODEL) (122) ( if i create users more ( like admins) than snusers )
        try:
            return SNUser.objects.get(userId=userId)
        except SNUser.DoesNotExist:
            raise AttributeError('such snuser doesnt exist')
    def get_dialog(self, chatId): # pk may be self (2) ( but userId from AUTH.USER_MODEL) (122) ( if i create users more ( like admins) than snusers )
        try:
            return DialogForSNUser.objects.get(id=chatId)
        except DialogForSNUser.DoesNotExist:
            raise AttributeError('such dialog doesnt exist')
    def get_conversation(self, chatId): # pk may be self (2) ( but userId from AUTH.USER_MODEL) (122) ( if i create users more ( like admins) than snusers )
        try:
            return ConversationForSNUser.objects.get(id=chatId)
        except ConversationForSNUser.DoesNotExist:
            raise AttributeError('such conversation doesnt exist')
    def get_chat(self, chatTypeId, chatId):
        serializer = None
        if(chatTypeId == "0"):
            chat = self.get_dialog(chatId)
            chat.calcLastMessageId() # посчитаем индекс с которого будет отсчет новых перед тем как отправить эти данные которые высчитаются в проперти
            chat.refresh_from_db()
            serializer = DialogFSNSerializer(chat) # , context={'request': self.request}
        else:
            chat = self.get_conversation(chatId)
            chat.calcLastMessageId() 
            chat.refresh_from_db()
            serializer = ConversationFSNSerializer(chat) 
        return serializer.data

    def createDialog(self, me, snuser): # another snuser and me (self) 
        dialogIds = [me.userId, snuser.userId]
        dialogIds.sort()
        uniqueStr = ','.join([str(elem) for elem in dialogIds])
        dialog = Dialog.objects.create(name=uniqueStr) # if not unique - raise exception - do not create new DialogForSNUser objects
        DialogForSNUser.objects.create(snuser=me, dialog=dialog, name=snuser.name, chatTypeId=0)
        DialogForSNUser.objects.create(snuser=snuser, dialog=dialog, name=me.name, chatTypeId=0)

    def createConversation(self, me, snusers, name): # many ids of snusers = queryset
        uniqueStr = f'{name}_{me.userId}'
        conversation = Conversation.objects.create(creator=me, name=uniqueStr)
        ConversationForSNUser.objects.create(snuser=me, conversation=conversation, isAdmin=True, name=name, chatTypeId=1)
        [ConversationForSNUser.objects.create(snuser=snuser, conversation=conversation, name=name, chatTypeId=1) for snuser in snusers]

    @responseDecorator
    def post(self, request, *args, **kwargs):
        response = {'created': False}
        try:
            me = self.get_user(request.user.id) 
            if isinstance(request.data['snusers'], list) == True: # snusers // name
                snusersInConversation = []
                for snuserId in request.data['snusers']:
                    snusersInConversation.append(self.get_user(snuserId))
                self.createConversation(me, snusersInConversation, request.data['name'])
            else:
                print('dialog creation')
                self.createDialog(me, self.get_user(request.data['snusers']))
            response['created'] = True 
        except Exception as er:
            print('some error')
            print(er)
            print()
            response = ({'created': False}, HTTP_400_BAD_REQUEST, {'errorMessage': str(er)})
        return response

    @responseDecorator
    def get(self, request, chatTypeId, chatId, format=None):
        return self.get_chat(chatTypeId, chatId)
        
    @responseDecorator
    def put(self, request, chatTypeId, chatId, format=None): 
        
        chat = self.getChatObject(chatTypeId, chatId)
        putData = request.data 
        response = {}
        if 'putType' in putData:

            if putData['putType'] == 'clear' : # or 'True'
                clearType = putData['clearType']
                if chat.clearByType(clearType) == True:
                    response['cleared'] = True
                else:
                    response['cleared'] = False

            elif putData['putType'] == 'rename': 
                newChatFSNName = putData['newChatName'] # rename chat locally only (globally always stay the same for unique field)
                serializer = None
                if chat.__class__ == ConversationForSNUser:
                    serializer = UpdateCFSNNameSerializer(chat, data={'name': newChatFSNName})
                elif chat.__class__ == DialogForSNUser:
                    serializer = UpdateDFSNNameSerializer(chat, data={'name': newChatFSNName})
                else:
                    raise TypeError(f'chat should be instance of ConversationForSNUser or DialogForSNUser and not {chat.__class__}')
                if serializer.is_valid(raise_exception=True):
                        serializer.save()
                response['renamed'] = True # can send 'name': serializer.data
            
            # only from conversation instances react can send
            elif putData['putType'] == 'toogleMemberStatus': # just send that key and then send snuserId (to toogle status)
                userId = putData['userId'] # memberId # memberStatus # userId => snuser.userId == user.id
                member = self.get_user(userId)
                if chat.toogleMemberStatus(member) == True:
                    response['toggled'] = True
                else:
                    response['toggled'] = False # if you arent creator - you ll get False in toggling
            
            # -----------------
            elif putData['putType'] == 'updateUnreadMsgs': # + index of offset from last global msg ( to save how mush new msgs doesnt readed yet from this chat) 
                lastGlobalReadMsgId = putData['lastGlobalReadMsgId'] 
            ######################################### in react just get last sorted msg in list of msgs in chat and then just get it id send here if 'local': False in last msg
                chat.updateUnreadMsgs(lastGlobalReadMsgId)
                response['lastMsgUpdated'] = True
            
            # only from conversation instances react can send
            elif putData['putType'] == 'addMember': 
                userId = putData['userId']
                member = self.get_user(userId)
                if chat.addMember(member) == True:
                    response['memberAdded'] = True
                else:
                    response['memberAdded'] = False 
            # only from conversation instances react can send
            elif putData['putType'] == 'removeMember': 
                userId = putData['userId']
                member = self.get_user(userId)
                if chat.removeMember(member) == True:
                    response['memberRemoved'] = True
                else:
                    response['memberRemoved'] = False

            # only from conversation instances react can send
            elif putData['putType'] == 'removeMemberMsgs': 
                userId = putData['userId']
                member = self.get_user(userId)
                # can catch there Http404 if there is no such conversation for user ( it would be an error brom react side )
                memberLC = member.conversations.get(conversation__id=chat.conversation.id) # look up for such id of global conversation
                if memberLC is None:
                    raise AttributeError('such member doesnt exist')

                if chat.removeAllMemberMsgs(memberLC) == True:
                    response['memberMsgsRemoved'] = True
                else:
                    response['memberMsgsRemoved'] = False

            # only from conversation instances react can send
            elif putData['putType'] == 'removeOneMemberMsg': 
                # если сам юзер локально удалил а глобально не удалил, то мы посути не сможем
                messageId = putData['messageId'] # global msg id # (delete it globally and locally for that user)
                # I SHOULDNT CREATE MSGS IS THERE IS NO SUCH # it solved !!!! i dont know how!!! what a shit is this
                findedGlobalMsg = ConversationMessage.objects.get(id=messageId) # TODO - faster search if i send snuser.userId with messageId -> cause search in that snusers query easier
                if findedGlobalMsg is None:
                    raise AttributeError('such global Msg doesnt exist')
                member = findedGlobalMsg.author # snuser
                # can catch there Http404 if there is no such conversation for user ( it would be an error brom react side )
                memberLC = member.conversations.get(conversation__id=chat.conversation.id) # look up for such id of global conversation
                if memberLC is None:
                    raise AttributeError('such member doesnt exist')
                if chat.removeOneMemberMsg(memberLC, findedGlobalMsg) == True:
                    response['memberMsgRemoved'] = True
                else:
                    response['memberMsgRemoved'] = False
            
            elif putData['putType'] == 'setChatPhoto': 
                newChatPhoto = putData['newChatPhoto']
                if chat.setChatPhoto(newChatPhoto) == True:
                    response['isChatPhotoChanged'] = True
                else:
                    response['isChatPhotoChanged'] = False


            else:
                raise KeyError('there is no available keys')
        else:
            raise KeyError('there is no key "putType" ')
        return response

    @responseDecorator
    def delete(self, request, chatTypeId, chatId, format=None):
        chat = self.getChatObject(chatTypeId, chatId)
        chat.deleteChat()
        print('deleteddd')
        status = HTTP_200_OK
        data = None
        return (data, status)

    def getChatObject(self, chatTypeId, chatId):
        if(chatTypeId == "0"):
            return self.get_dialog(chatId)
        elif(chatTypeId == "1"):
            return self.get_conversation(chatId)
        else:
            raise KeyError(f'chatTypeId should be 1 or 0 not {chatTypeId}')