# Generated by Django 3.0.6 on 2020-08-28 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SNUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.TextField(default='')),
                ('photos', models.TextField(default="{'small' : null, 'large' : null}")),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('userId', models.IntegerField(blank=True)),
                ('lookingForAJob', models.BooleanField(default=False)),
                ('lookingForAJobDescription', models.TextField(default='')),
                ('fullname', models.TextField(default='')),
                ('contacts', models.TextField(default="{'github': '', 'vk': '', 'facebook': '', 'instagram': '', 'twitter': '', 'website': '', 'youtube': '', 'mainLink': ''}")),
                ('follows', models.ManyToManyField(related_name='followed_by', to='snusers.SNUser')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
