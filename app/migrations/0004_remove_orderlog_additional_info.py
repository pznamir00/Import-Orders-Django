# Generated by Django 3.2.6 on 2021-09-18 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20210918_1405'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderlog',
            name='additional_info',
        ),
    ]
