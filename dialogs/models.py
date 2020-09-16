from django.db import models
from snusers.models import SNUser
# Create your models here.
from django.apps import apps
# from django_postgres_extensions.models.functions import ArrayRemove
# from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
import time
from  datetime import datetime

from django.utils.timezone import make_aware
import pytz
from django.utils.timezone import activate
from django.conf import settings



class CastableModelMixin:
    """
    Add support to cast an object to its final class
    """

    def cast(self):
        cls = self.__class__
        subclasses = cls.all_subclasses()

        if len(subclasses) == 0:
            return self

        for subclass in subclasses:
            try:
                obj = getattr(self, subclass._meta.model_name, None)
                if obj is not None:
                    # select_related doesn't fill child with parent relateds
                    descriptors = [getattr(cls, field.name)
                                   for field in cls._meta.get_fields()
                                   if field.is_relation and field.many_to_one]
                    for descriptor in descriptors:
                        if descriptor.is_cached(self):
                            setattr(obj,
                                    descriptor.cache_name,
                                    getattr(self, descriptor.cache_name))
                    if hasattr(self, '_prefetched_objects_cache'):
                        obj._prefetched_objects_cache = \
                            self._prefetched_objects_cache
                    return obj
            except ObjectDoesNotExist:
                pass

        return self

    @classmethod
    def all_subclasses_model_names(cls):
        model_names = []
        for subclass in cls.all_subclasses():
            if not (subclass._meta.proxy or subclass._meta.abstract):
                model_names.append(subclass._meta.model_name)
        return model_names

    @classmethod
    def all_subclasses(cls):
        return [g for s in cls.__subclasses__() for g in s.all_subclasses()] + cls.__subclasses__()

    @property
    def model(self):
        return self.cast()._meta.model_name

    @property
    def verbose_name(self):
        return self.cast()._meta.verbose_name.capitalize()



class Dialog(models.Model):
    name = models.TextField(unique=True) # will store name of opponent of user that create chat

class Conversation(models.Model):
    name = models.TextField(unique=True) # will store name that will be given by creator ( if after that create feature that add users to conv after creation of conv)
    creator = models.ForeignKey(SNUser, on_delete=models.CASCADE, related_name='creatorOfConversations')# создатель бесед
    chatPhoto = models.TextField(default="{'small' : null, 'large' : null}") # there will be url at first

class IntermediateLayerForMessaging(models.Model, CastableModelMixin):
    lastReadMessageId = models.IntegerField(default=0)

    startMsgId = models.IntegerField(default=0)  

    chatTypeId = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def checkIsLessRFIS(self, queryset, readFromIndexStart):
        if readFromIndexStart is None: #  в самом начале до прогрузке все сообщения возвращаем (чтобы индекс взять с 10 с конца от всех сообщений) (тупо, очень тупо(((  
            return [msg.id for msg in queryset]
        arr = []
        for msg in queryset: 
            if msg.id < readFromIndexStart:
                arr.append(msg.id) 
        return arr  
    def readFromIndexCalcNext(self, readFromIndexStart): 
        msgsPerOneLoad = 10
        index=None 
        oldLocalMessages, oldGlobalMessages = self.getOldGlobalMsgs 
        arr1 = self.checkIsLessRFIS(oldLocalMessages, readFromIndexStart)
        arr2 = self.checkIsLessRFIS(oldGlobalMessages, readFromIndexStart) 
        


        sortedOldMsgs = sorted(arr1+arr2, reverse=True) # descending (hope) 
        if len(sortedOldMsgs) >= msgsPerOneLoad: 
            index = sortedOldMsgs[msgsPerOneLoad-1]
        elif len(sortedOldMsgs) > 0:
            index = sortedOldMsgs[len(sortedOldMsgs) - 1] # get oldest msg from chat(if there is less then 10 msgs in chat)
        else:
            if readFromIndexStart is None: # если только начало чтения сообщений(первый лоад - то индекс = 0 если нет сообщений)
                index = 0
            else:
                index = readFromIndexStart
        # print(index)
        return index




    @property 
    def readFromIndexBefore(self):  
        return None 


# should also add def to calc readFromIndexCalc for each download of msgs or other content
    @property
    def readFromIndex(self):  
        return self.readFromIndexCalcNext(None) 


    @property
    def chatTimeStamp(self):
        # print(self.lastMessage)
        if 'sended' in self.lastMessage: # last message is not None
            return self.lastMessage['sended']
        else:
            return self.toUnixTime(self.created)


    @property
    def members(self):
        if self.__class__ == ConversationForSNUser: 
            return [{'name': cfns.snuser.name, 'photos': cfns.snuser.photos, 'id': cfns.snuser.userId, 'isAdmin': cfns.isAdmin} for cfns in self.conversation.snusers.all()]
        else:
            return [{'name': dfns.snuser.name, 'photos': dfns.snuser.photos, 'id': dfns.snuser.userId} for dfns in self.dialog.snusers.all()]

    @property
    def lastMessage(self):
        try:
            if( self.__class__ == ConversationForSNUser ):
                if self.conversation.messages.count() > 0:
                    if self.conversation.messages.last().id > self.startMsgId:
                        lastGlobal = self.conversation.messages.exclude(author__userId=self.snuser.userId).last() # None 
                        lastLocal = self.myMsgs().last() # None 
                        isLocal = False
                        
                        if lastLocal is not None and lastGlobal is not None:
                            if lastGlobal.id > lastLocal.id:
                                lastMsg = lastGlobal
                            else:
                                lastMsg = lastLocal
                                isLocal = True
                        elif lastLocal is not None:
                            lastMsg = lastLocal
                        elif lastGlobal is not None:
                            lastMsg = lastGlobal
                        else:
                            lastMsg = None

                        return {} if lastMsg is None else {'body': lastMsg.body, 'id': lastMsg.id, 'sended': self.toUnixTime(lastMsg.sended), 'authorName': lastMsg.author.name, 'local': isLocal} 
                  # all global msgs in conv
            else:
                if self.dialog.messages.count() > 0:
                    if self.dialog.messages.last().id > self.startMsgId:
                        lastGlobal = self.dialog.messages.exclude(author__userId=self.snuser.userId).last()
                        lastLocal = self.myMsgs().last()
                        isLocal = False  
                        if lastLocal is not None and lastGlobal is not None:
                            if lastGlobal.id > lastLocal.id:
                                lastMsg = lastGlobal
                            else:
                                lastMsg = lastLocal
                                isLocal = True
                        elif lastLocal is not None:
                            lastMsg = lastLocal
                        elif lastGlobal is not None:
                            lastMsg = lastGlobal
                        else:
                            lastMsg = None


                        return {} if lastMsg is None else {'body': lastMsg.body, 'id': lastMsg.id, 'sended': self.toUnixTime(lastMsg.sended), 'authorName': lastMsg.author.name, 'local': isLocal}
        except Exception as er:
            print('Wierd Unexpected Error')
            print(er)
        return {}


    @property
    def chatPhoto(self):
        try:
            if( self.__class__ == ConversationForSNUser ):
                return self.conversation.chatPhoto # small and large too 
            else:
                return self.dialog.snusers.exclude(snuser=self.snuser)[0].snuser.photos
        except Exception as er:
            print('Wierd Unexpected Error')
            print(er)
        return "{'small' : null, 'large' : null}"
 

    def toUnixTime(self, value):
        """ to_unix_time_representation_for_js """
        return int(time.mktime(value.timetuple())) 

    def strTime(self, time): 
        return time.strftime('%Y-%m-%d %H:%M %Z')

    @property
    def firstNewMsgID(self):
        try:
            newLocalMessages, newGlobalMessages = self.getNewGlobalMsgs # blue color
            newMsgs = self.serializeMsgs(newLocalMessages, newGlobalMessages, False) # get list of objects
            print("firstNewMsgID")
            if(len(newMsgs) == 0):
                print("no new msgs for u in chat")
                return None
            firstNM = sorted(newMsgs, key=lambda arr: arr['sended'])[0] # first elem of this new msgs list 
            print(firstNM['id'])
            return firstNM['id']
        except Exception as ex:
            print(ex)
            return None

    def serializeMsgs(self, localMsgs, globalMsgs, msgViewed): # msgViewed- old - true // new - false 
        # just send fileId ( if they not None and if they not loaded in IDB yet -> run Worker to load that files)
        arr1 = [{'id': msg.id, 'body': msg.body, 'sended': self.toUnixTime(msg.sended), 
            'edited': self.toUnixTime(msg.edited), 'authorName': msg.author.name, 'authorId': msg.author.userId, 
            'local':True, 'msgViewed': msgViewed, "fileId": msg.fileId } for msg in localMsgs] # "isLoadMedia": msg.isLoadMedia, 

        arr2 = [ {'id': gM.id, 'body': gM.body, 'sended': self.toUnixTime(gM.sended), 
            'edited': self.toUnixTime(gM.edited), 'authorName': gM.author.name, 'authorId': gM.author.userId, 
            'local':False, 'msgViewed': msgViewed, "fileId": gM.fileId } for gM in globalMsgs] # "file": gM.loadMedia
        return arr1 + arr2

    def getGlobalMsgs(self, msgsType):
        try:
            returnList = []
            if msgsType == 'new':
                returnList.append([]) # locally cant be new
            elif msgsType == 'old':
                returnList.append(self.myMsgs()) # locally can be old
            else:
                raise ValueError('msgsType should be "new" or "old"')
            listOfLocalSubs = [msg.globalMsg.id for msg in self.myMsgs()] # but if self msgs cleaned ( so then my global should be muted for me - so use exclude global msgs by authorId==self.snuser.userId too)
            # print("listOfLocalSubs")
            # print(listOfLocalSubs)
            if( self.__class__ == ConversationForSNUser ): 
                # вернет ли оно 2 списка из id TODO check
                if msgsType == 'new': 
                    greaterThen = self.lastReadMessageId if self.lastReadMessageId > self.startMsgId else self.startMsgId
                    returnList.append(self.conversation.messages.filter(id__gt=greaterThen).exclude(id__in=listOfLocalSubs).exclude(author__userId=self.snuser.userId))
                elif msgsType == 'old': 
                    returnList.append(self.conversation.messages.filter(Q(id__gt=self.startMsgId) & Q(id__lte=self.lastReadMessageId)).exclude(id__in=listOfLocalSubs).exclude(author__userId=self.snuser.userId))
                return returnList
            else:
                if msgsType == 'new':
                    greaterThen = self.lastReadMessageId if self.lastReadMessageId > self.startMsgId else self.startMsgId
                    returnList.append(self.dialog.messages.filter(id__gt=greaterThen).exclude(id__in=listOfLocalSubs).exclude(author__userId=self.snuser.userId))
                elif msgsType == 'old': 
                    returnList.append(self.dialog.messages.filter(Q(id__gt=self.startMsgId) & Q(id__lte=self.lastReadMessageId)).exclude(id__in=listOfLocalSubs).exclude(author__userId=self.snuser.userId))
 
                return returnList
        except AttributeError as er:
            print('looks like there is no messages in chat yet GGM')
            print(er)
        except Exception as er:
            print('Wierd Unexpected Error')
            print(er)
        return [[],[]]

    @property
    def getOldGlobalMsgs(self): # if you dont delete global cache locally before it - index will be 1
        """return queryset or None"""  
        msgsType = 'old' 
        return self.getGlobalMsgs(msgsType)

    @property
    def getNewGlobalMsgs(self):
        """return queryset or None"""  
        msgsType = 'new'
        newMsgs = self.getGlobalMsgs(msgsType) 
        return newMsgs
        

    @property
    def getCountOfNewGlobalMsgs(self):
        """return some int value or None""" 
        try:
            NewMsgs = self.getNewGlobalMsgs 
            return 0 if isinstance(NewMsgs[1], list) else NewMsgs[1].count() # count only global msgs ( cause local stay the same )
        except AttributeError as er:
            print('looks like there is no messages in chat yet CGM')
            print(er)
        except Exception as er:
            print('Wierd Unexpected Error')
            print(er)
        return None

    def updateUnreadMsgs(self, lastGlobalReadMsgId): # just set last read msgs as last global and thats all
        if( self.__class__ == ConversationForSNUser ):
            self.lastReadMessageId = lastGlobalReadMsgId
        else: 
            self.lastReadMessageId = lastGlobalReadMsgId
        self.save()

    def calcLastMessageId(self):
        """ 
        always return some int value 
        for calc new self.lastReadMessageId
        """ 
        lastReadMessageId = self.lastReadMessageId # if stilll None read all from that global chat ( add field and add to this field )
        try:
            if(len(self.myMsgs()) > 0):
                last = self.myMsgs().last() 
                if(last.globalMsg.id > self.lastReadMessageId): # in locals last id = 0 //  
                    lastReadMessageId = last.globalMsg.id
        except AttributeError as er:
            print('\n')
            print('IntermediateLayerForMessaging . lastMessageId error in class ' + self.__class__+ ' and instance '+ self)
            print('\n')
            print(er)
            print('\n')
        except Exception as er:
            print('Wierd Unexpected Error')
            print(er)
        self.lastReadMessageId = lastReadMessageId
        self.save()
    
    class Meta:
        abstract = True

    # 2 feature
    def clearAllMsgsGlobal(self): # isAdmin if CFNS
        """ return True or False or None(if no msgs in chat yet)"""
        try:
            if( self.__class__ == ConversationForSNUser ):
                if(self.isAdmin == True):
                    for snuser in self.conversation.snusers.all():
                        for msg in snuser.myMsgs():
                            msg.globalMsg.delete()
                            msg.delete()
                        for msgG in snuser.snuser.globalConversations.all():
                            msgG.delete()
                else:
                    return False
            else:
                for snuser in self.dialog.snusers.all():
                        for msg in snuser.myMsgs():
                            msg.globalMsg.delete()
                            msg.delete()
                        for msgG in snuser.snuser.globalDialogs.all():
                            msgG.delete()
            return True
        except AttributeError as er:
            print('looks like there is no messages in chat yet')
            print(er)
        except Exception as er:
            print('Wierd Unexpected Error')
            print(er)
        return None

    def clearAllMsgsLocal(self):
        """ return True or None(if no msgs in chat yet)"""
        try:
            if( self.__class__ == ConversationForSNUser ):
                self.startMsgId = self.startMsgId if self.conversation.messages.all() is None else self.conversation.messages.all().last().id # last global
            else:
                self.startMsgId = self.startMsgId if self.dialog.messages.all() is None else self.dialog.messages.all().last().id # last global
            print("clearAllMsgsLocal . startMsgId")
            print(self.startMsgId)
            self.clearMyMsgsLocal()
            self.save()
            return True
        except AttributeError as er:
            print('looks like there is no messages in chat yet')
            print(er)
        except Exception as er:
            print('Wierd Unexpected Error')
            print(er)
        return None

    def clearMyMsgsGlobal(self):
        """ return True or None(if no msgs in chat yet)"""
        try:
            # delete my local msgs and linked to them my global
            for msg in self.myMsgs():
                msg.globalMsg.delete() # CM // DM
                msg.delete() # MCM // MDM
            
            # delete my global msgs that are linked directly to my snuser instance // если до этого удалял уже локальные ( и старые глобальные сообщения недосягаемы через локальные )
            if( self.__class__ == ConversationForSNUser ):
                for msg in self.snuser.globalConversations.all():
                    msg.delete()
            else:
                for msg in self.snuser.globalDialogs.all():
                    msg.delete()
            # TODO
            # print(self.myMsgs())
            return True
        except AttributeError as er:
            print('looks like there is no messages in chat yet')
            print(er)
        except Exception as er:
            print('Wierd Unexpected Error')
            print(er)
        return None

    def clearMyMsgsLocal(self): # delete all self messages
        """ return True or None(if no msgs in chat yet)"""
        try: 
            self.myMsgs().delete()
            return True
        except AttributeError as er:
            print('looks like there is no messages in chat yet')
            print(er)
        except Exception as er:
            print('Wierd Unexpected Error')
            print(er)
        return None

    def myMsgs(self): 
        return self.messages.all()

    def clearByType(self, clearType):
        clearTypes = {'myLocal': self.clearMyMsgsLocal, 'myGlobal': self.clearMyMsgsGlobal, 'allLocal': self.clearAllMsgsLocal, 'allGlobal': self.clearAllMsgsGlobal}
        if clearType in clearTypes: 
            if clearTypes[clearType]() == True:
                return True
        return False

    def deleteChat(self):
        if self.__class__ == ConversationForSNUser:
            print('conv deletion')
            print(self.conversation.creator)
            print(self.snuser)
            if self.conversation.creator == self.snuser: # not admins allowed to delete chat - onle creator
                self.clearAllMsgsGlobal()
                self.conversation.delete()
            else:
                # cant delete conv - only can delete local msgs from conv (cause ) надо добавить ключ - который удалить себя из конверсейшн а только потом удалим конв фор сн юзер ( ибо иначе )
                self.clearMyMsgsLocal()
                self.delete()
            print('\n\nconv deleted\n\n')
        else:
            print('dialog deletion')
            self.clearAllMsgsGlobal()
            self.dialog.delete()
            print('dialog deleted')

            

    # 1 feature
    def isItMyMessage(self, msg):  # проверка на Message.author и self == request.user в view
        if(msg.author.userId==self.snuser.userId):
            return True
        else:
            return False

    # if ConversationForSNUser instance -> so we search id of message in ConversationMessage
    def editMyMessage(self, newMessageBody, message): # message can be like DialogMessage so like ConversationMessage
        if(self.isItMyMessage(message)):
            message.globalMsg.body = newMessageBody
            message.globalMsg.save()
            message.body = newMessageBody
            message.save()

    # we do not user message.id but message itself   === message = Message.objects.get(id=messageId)
    def deleteMyMessage(self, message):
        print('deleteMsg')
        if(self.isItMyMessage(message)):
            message.globalMsg.delete() # delete globally
            message.delete() # delete locally

    def createNewMessage(self, messageBody, fileId=None):
        try: 
            localMsg = None 
            if self.__class__ == ConversationForSNUser:
                if fileId is None:
                    localMsg = MyConversationMessage.objects.create(body=messageBody, snuser=self)
                    ConversationMessage.objects.create(body=messageBody, snuserGlobal=self.conversation, localMessage=localMsg, author=self.snuser)
                else: 
                    localMsg = MyConversationMessage.objects.create(body=messageBody, snuser=self, fileId=fileId) # cause it already loaded to users localStorage (indexedDb or not???)
                    ConversationMessage.objects.create(body=messageBody, snuserGlobal=self.conversation, localMessage=localMsg, author=self.snuser, fileId=fileId) 
                self.lastReadMessageId += 1
            else:
                if fileId is None:
                    localMsg = MyDialogMessage.objects.create(body=messageBody, snuser=self)
                    DialogMessage.objects.create(body=messageBody, snuserGlobal=self.dialog, localMessage=localMsg, author=self.snuser)
                else: 
                    localMsg = MyDialogMessage.objects.create(body=messageBody, snuser=self, fileId=fileId)
                    DialogMessage.objects.create(body=messageBody, snuserGlobal=self.dialog, localMessage=localMsg, author=self.snuser, fileId=fileId)
                
                self.lastReadMessageId += 1 
        except Exception as ex:
            print('trying to create msg')
            print(ex)


class ConversationForSNUser(IntermediateLayerForMessaging):
    name = models.TextField()
    snuser = models.ForeignKey(SNUser, on_delete=models.CASCADE, related_name='conversations') # учасник бесед
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='snusers') 
    isAdmin = models.BooleanField(default=False)


    def setChatPhoto(self, newChatPhoto):
        if(self.conversation.creator == self.snuser):
            self.conversation.chatPhoto = newChatPhoto
            self.conversation.save() 
            return True
        return False

    def toogleMemberStatus(self, snuser):
        # print('set an admin')
        if(self.conversation.creator == self.snuser): 

            memberConversation = snuser.conversations.get(conversation__id = self.conversation.id)
            if(memberConversation.isAdmin == False):
                memberConversation.isAdmin = True
                memberConversation.save()
            else:
                memberConversation.isAdmin = False
                memberConversation.save()
            return True
        return False

    def removeMember(self, snuser): 
        if(self.isAdmin == True):
            self.conversation.snusers.get(snuser__userId=snuser.userId).delete()
            return True
        return False

    def addMember(self, snuser): 
        if(self.isAdmin == True):
            ConversationForSNUser.objects.create(name=self.name, snuser=snuser, conversation=self.conversation)
            return True
        return False
        

    def removeAllMemberMsgs(self, memberLC): #memberLocalConversaion 
        if self.conversation.creator.userId == self.snuser.userId:
            memberLC.clearMyMsgsGlobal()
            return True
        elif self.isAdmin == True:
            if self.conversation.creator.userId == memberLC.snuser.userId:
                return False
            memberLC.clearMyMsgsGlobal()
            return True
        else:
            return False

    def deleteMemberMessageByAdmin(self, globalMessage):
        if globalMessage.localMessage is not None:
            globalMessage.localMessage.delete() 
        globalMessage.delete()
    
    def removeOneMemberMsg(self, memberLC, globalMessage): #memberLocalConversaion
        print(f'removeOneMemberMsg {memberLC.snuser.name} : {globalMessage.body}')
        if self.conversation.creator.userId == self.snuser.userId:
            memberLC.deleteMemberMessageByAdmin(globalMessage)
            return True
        elif self.isAdmin == True:
            if self.conversation.creator.userId == memberLC.snuser.userId:
                return False
            memberLC.deleteMemberMessageByAdmin(globalMessage)
            return True
        else:
            return False



class DialogForSNUser(IntermediateLayerForMessaging):
    name = models.TextField()
    snuser = models.ForeignKey(SNUser, on_delete=models.CASCADE, related_name='dialogs') # ds_fsnuser
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name='snusers') # ds_fsnuser


# import uuid
class File(models.Model):
    file = models.TextField()
    name = models.CharField(max_length=300)
    format = models.CharField(max_length=300)
    isImage=models.BooleanField(default=False) 
    def __str__(self):
        return self.name
 
class Message(models.Model, CastableModelMixin): 
    fileId = models.IntegerField(blank=True, null=True)

    body = models.TextField()
    sended = models.DateTimeField(auto_now_add=True) # created
    edited = models.DateTimeField(auto_now=True) # updated 

    class Meta:
        abstract = True


class MyDialogMessage(Message):
    snuser = models.ForeignKey(DialogForSNUser, on_delete=models.CASCADE, related_name='messages') # DialogForSNUser.messages.all()
    
    @property
    def dialog(self):
        return self.snuser.dialog
    
    @property
    def author(self):
        return self.snuser.snuser

class MyConversationMessage(Message):
    snuser = models.ForeignKey(ConversationForSNUser, on_delete=models.CASCADE, related_name='messages') # ConversationForSNUser.messages.all()

    @property
    def conversation(self):
        return self.snuser.conversation
    
    @property
    def author(self):
        return self.snuser.snuser


class DialogMessage(Message):
    snuserGlobal = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name='messages') # не в свеом кеше а в общем у самого диалога
    localMessage = models.OneToOneField(MyDialogMessage, on_delete=models.SET_NULL, related_name='globalMsg', null=True)
    author = models.ForeignKey(SNUser, on_delete=models.SET_NULL, related_name='globalDialogs', null=True) 
 
 
class ConversationMessage(Message):
    snuserGlobal = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    localMessage = models.OneToOneField(MyConversationMessage, on_delete=models.SET_NULL, related_name='globalMsg', null=True)
    author = models.ForeignKey(SNUser, on_delete=models.SET_NULL, related_name='globalConversations', null=True) 
 



 