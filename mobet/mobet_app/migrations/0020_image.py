# Generated by Django 3.0.5 on 2020-05-19 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobet_app', '0019_auto_20200517_1453'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='usr')),
            ],
        ),
    ]