# Generated by Django 3.0.5 on 2020-05-17 14:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobet_app', '0018_auto_20200517_1452'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='participatedlist',
            options={'ordering': ('ROOMNUM_ID', '-LEFTMONEY')},
        ),
    ]
