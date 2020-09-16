from django.contrib.auth.models import User # get_user_model  User = get_user_model()
User.objects.create_superuser('admin', 'billyrusslee@gmail.com', '111')
print('\n\nMain ADMIN created\n\n')

User.objects.create_superuser('max', 'billyrusslee@gmail.com', '111')

User.objects.create_superuser('me', 'billyrusslee@gmail.com', '111')
print('\n\nOther ADMINs created\n\n')