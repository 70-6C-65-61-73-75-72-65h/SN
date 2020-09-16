from django.contrib.auth import get_user_model
from snusers.models import SNUser

User = get_user_model()

import sys, os

def populate_snusers(snusers):
    for i in range(snusers['num_snusers']):
        username = f'{snusers["overal_name"]}_{i}'
        user_obj = User(username = username,\
                email = f'{username}{snusers["overal_mail"]}')
        user_obj.set_password(snusers['password'])
        user_obj.save()
        user_obj.refresh_from_db()
        try:
            sn_user_obj = SNUser(userId=user_obj.id, lookingForAJob=snusers['lookingForAJob'], lookingForAJobDescription=snusers['lookingForAJobDescription'], fullname=user_obj.username, contacts=snusers['contacts'], name=user_obj.username, status=snusers['status'], photos=snusers['photos'])
            sn_user_obj.save()
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno) 


def main(snusers):
    print(f'populate {snusers["num_snusers"]} snusers')
    populate_snusers(snusers)
    print('popoulation was ended')


num_snusers = 21
overal_name = 'Mexus'
overal_mail = '@gmail.com'
password = 'hello111'
status = 'Nothing'
photos = "{'large': null, 'small': 'https://i.pinimg.com/originals/03/4d/64/034d64236d0bff434c25ae14b76c205b.jpg'}"

lookingForAJob = False
lookingForAJobDescription = 'Nothing'
# fullname = 'John Doe'
contacts = "{'github': '', 'vk': '', 'facebook': '', 'instagram': '', 'twitter': '', 'website': '', 'youtube': '', 'mainLink': ''}"
snusers = {"num_snusers": num_snusers, "overal_name":overal_name, "overal_mail":overal_mail, \
        "password": password, "status": status, "photos": photos, \
            "lookingForAJob": lookingForAJob, "lookingForAJobDescription": lookingForAJobDescription, \
                "contacts": contacts}
main(snusers)