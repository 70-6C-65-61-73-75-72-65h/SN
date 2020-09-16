from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model



from rest_framework.serializers import (
    CharField,
    EmailField,
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError, 
    BooleanField
    )


User = get_user_model()


class UserCreateSerializer(ModelSerializer):

    email = EmailField(label='Email Address')
    email2 = EmailField(label='Confirm Email')

    status = CharField(default='')
    photos = CharField(default="{'small' : null, 'large' : null}")

    lookingForAJob = BooleanField(default=False)
    lookingForAJobDescription = CharField(default='')
    fullname = CharField(default='')
    contacts = CharField(default="{'github': '', 'vk': '', 'facebook': '', 'instagram': '', 'twitter': '', 'website': '', 'youtube': '', 'mainLink': ''}")

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'email2',
            'password',
            'status',
            'photos',
            # 'follows',
            'lookingForAJob',
            'lookingForAJobDescription',
            'fullname',
            'contacts'
        ]
        extra_kwargs = {"password":
                            {"write_only": True}
                            }

    def validate_email(self, value):  # validate + _ + field_name ( self, value)
        data = self.get_initial()
        email1 = data.get("email2")
        email2 = value
        if email1 != email2:
            raise ValidationError("Emails must match.")
    
        user_qs = User.objects.filter(email=email2)
        if user_qs.exists():
            raise ValidationError("This user has already registered.")
        return value

    def create(self, validated_data):
        from snusers.models import SNUser

        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        
        user_obj = User(
                username = username,
                email = email
            )
        user_obj.set_password(password)
        user_obj.save()

        status = validated_data['status']
        photos = validated_data['photos']

        lookingForAJob = validated_data['lookingForAJob']
        lookingForAJobDescription = validated_data['lookingForAJobDescription']
        fullname = user_obj.username # then can be changed on other full name (SuperFucker ->>> John Doe)
        contacts = validated_data['contacts']

        sn_user_obj = SNUser(userId=user_obj.id, lookingForAJob=lookingForAJob, lookingForAJobDescription=lookingForAJobDescription,\
            fullname=fullname, contacts=contacts, name=username, status=status, photos=photos)
        sn_user_obj.save()

        return validated_data

 