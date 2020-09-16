from rest_framework.serializers import (
    CharField,
    EmailField,
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError, 
    BooleanField,
    HyperlinkedModelSerializer
    )
 
from snusers.models import SNUser

# from rest_framework.fields import CurrentUserDefault



class ProfileSerializer(ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        super(ProfileSerializer, self).__init__(*args, **kwargs)
        if 'data' in kwargs: # TRUE if method PUT
            fields = kwargs['data']
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    userRelation = SerializerMethodField()

    class Meta:
        model = SNUser
        fields = [
            'id',
            'userId',
            
            'name',
            'slug',

            'status',
            'photos',
            'userRelation',

            'lookingForAJob',
            'lookingForAJobDescription',
            'fullname',
            'contacts'
            ]

    def get_userRelation(self, obj): 
        try:
            user = self.context["request"].user 
            snuser = SNUser.objects.get(userId=user.id)
            # print(snuser)
            return snuser.userRelation(obj) # am i followed that snuser
        except SNUser.DoesNotExist: # if IAM admin - false // cause there is no snuser model for admins
            return False




# PUT /profile/photo
# ProfileUpdatePhotoSerializer
class ProfilePhotoSerializer(ModelSerializer):
    """ ProfileUpdatePhotoSerializer  -- PUT /profile/photo """
    photos = CharField(required=True, allow_blank=False, allow_null=False)

    class Meta:
        model = SNUser
        fields = [
            'photos', 
        ]

# PUT /profile/status
# ProfileUpdateRetrieveStatusSerializer - PURSS
class ProfileStatusSerializer(ModelSerializer):
    """ ProfileUpdateRetrieveStatusSerializer -- PUT /profile/status -- GET /profile/status/{userId} """
    status = CharField(required=True, allow_blank=False, allow_null=False)

    class Meta:
        model = SNUser
        fields = [
            'status',
        ]
