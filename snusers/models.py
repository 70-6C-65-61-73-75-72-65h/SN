from django.db import models

from django.contrib.postgres.fields import JSONField
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


from django.contrib.auth import get_user_model
User = get_user_model()

class SNUser(models.Model):
    ### for 127.0.0.1:4000:/users/
    
    # user = models.OneToOneField(User, on_delete=models.CASCADE) # may not nedded ( cause we link it with userId)

    name = models.CharField(max_length=255) # from user.username
    status = models.TextField(default='') # non required
    # photos = JSONField(default=dict)
    photos = models.TextField(default="{'small' : null, 'large' : null}") # non required

    follows = models.ManyToManyField('SNUser', related_name='followed_by')


    # followed = models.BooleanField(default=False) # non required
    slug = models.SlugField(unique=True, blank=True) # non required
 

    userId = models.IntegerField(blank=True) # from user.id

    lookingForAJob = models.BooleanField(default=False) # non required
    lookingForAJobDescription = models.TextField(default='') # non required
    fullname = models.TextField(default='') # non required
    contacts = models.TextField(default="{'github': '', 'vk': '', 'facebook': '', 'instagram': '', 'twitter': '', 'website': '', 'youtube': '', 'mainLink': ''}") # non required


    def getDialogs(self):
        try:
            return self.dialogs.all()
        except Exception as ex:
            print('\neee boiiiiii\n')
            print(ex)
            return []

    def getConversations(self):
        try:
            return self.conversations.all()
        except Exception as ex:
            print('getConversations error')
            print(ex)
            return []
   
    # @property
    def addToFollow(self, snuser):
        """ uses SNUser.id (not userId) """
        try:
            self.follows.add(snuser)
            self.save()
        except Exception as ex:
            print(ex)
            return False
        return True

    # @property
    def removeFromFollow(self, snuser):
        """ uses SNUser.id (not userId) """
        try:
            self.follows.remove(snuser)
            self.save()
        except Exception as ex:
            print(ex)
            return False
        return True



    def subscribers(self):
        return list(set(self.followed_by.all()) - set(self.follows.all()))
    def subscriptions(self): 
        return list(set(self.follows.all()) - set(self.followed_by.all()))
    def friends(self):
        return list(set(self.follows.all()) & set(self.followed_by.all()))

    def checkRelation(self, function, snuser):
        if snuser in function.__get__(self, self.__class__)():
            return True
        return False
        
    def isSubscriber(self, snuser):
        return self.checkRelation(self.subscribers, snuser)
    def isSubscription(self, snuser):
        return self.checkRelation(self.subscriptions, snuser)
    def isFriend(self, snuser):
        return self.checkRelation(self.friends, snuser)

    def userRelation(self, snuser):
        if(snuser == self):
            return False
        if(self.isSubscriber(snuser)):
            return 'subscriber'
        elif(self.isSubscription(snuser)):
            return 'subscription'
        elif(self.isFriend(snuser)):
            return 'friend'
        else:
            return None
        





    def __str__(self):
        return self.slug

    class Meta:
        ordering = ["-id"]
 


def create_slug(instance, new_slug=None):
    """ create slug to url, from title or title with adding to it the id"""
    slug = slugify(instance.name.lower())
    if new_slug is not None:
        slug = new_slug
    qs = SNUser.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(instance.name.lower(), qs.first().id) # markus-1  markus-1-2
        return create_slug(instance, new_slug=new_slug)
    return slug

# creation slug right before PROFILE creation
@receiver(pre_save, sender=SNUser)
def pre_save_sn_user_receiver(sender, instance, *args, **kwargs):
    """
    Method pre_save receiver of Profile model to generate
    slug
    """
    if not instance.slug:
        slug = create_slug(instance)

        instance.slug = slug

