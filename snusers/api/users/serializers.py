from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField, 
    )


from snusers.models import SNUser 

snuser_detail_url = HyperlinkedIdentityField(
        view_name='snusers-api:detail',
        lookup_field='userId'
        )

class SNUserListDetailSerializer(ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        super(SNUserListDetailSerializer, self).__init__(*args, **kwargs)

        if 'data' in kwargs: # TRUE if method POST
            fields = kwargs['data']
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    url = snuser_detail_url
    userRelation = SerializerMethodField()
    
    class Meta:
        model = SNUser
        fields = [
            'url',
            
            'id',
            'name',
            'status',
            'photos',
            'userRelation',

            'slug',

            'userId',
            'lookingForAJob',
            'lookingForAJobDescription',
            'fullname',
            'contacts',
        ]

    def get_userRelation(self, obj):
        try: 
            user = self.context["request"].user 
            snuser = SNUser.objects.get(userId=user.id)
            # print(snuser)
            return snuser.userRelation(obj) # am i followed that snuser
        except SNUser.DoesNotExist: # if IAM admin - false // cause there is no snuser model for admins
            return False



class ProfileFollowSerializer(ModelSerializer):
    """ ProfileFollowSerializer  -- Get /follow/userId """ 
    userRelation = SerializerMethodField()

    class Meta:
        model = SNUser
        fields = [
            'userRelation',
        ]

    def get_userRelation(self, obj): # obj - user to check  ( am i followed or not ) // obj - created object after serialization
        try:
            user = self.context["request"].user 
            snuser = SNUser.objects.get(userId=user.id) 
            return snuser.userRelation(obj) # am i followed that snuser
        except SNUser.DoesNotExist: # if IAM admin - false // cause there is no snuser model for admins
            return False


""""

from posts.models import Post
from posts.api.serializers import PostDetailSerializer


data = {
    "title": "Yeahh buddy",
    "content": "New content",
    "publish": "2016-2-12",
    "slug": "yeah-buddy",
    
}

obj = Post.objects.get(id=2)
new_item = PostDetailSerializer(obj, data=data)
if new_item.is_valid():
    new_item.save()
else:
    print(new_item.errors)


"""