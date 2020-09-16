from django.contrib import admin
from .models import Conversation, Dialog, DialogForSNUser, ConversationForSNUser, MyDialogMessage, MyConversationMessage, DialogMessage, ConversationMessage, File

admin.site.register(Conversation)
admin.site.register(Dialog)
admin.site.register(DialogForSNUser)
admin.site.register(ConversationForSNUser) 
admin.site.register(MyDialogMessage)
admin.site.register(MyConversationMessage)
admin.site.register(DialogMessage)
admin.site.register(ConversationMessage)
admin.site.register(File)
