# Generated by Django 3.2.6 on 2021-09-18 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_userprofile_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(blank=True, choices=[('1', 'Client'), ('2', 'Executor'), ('3', 'Planner'), ('4', 'Management')], max_length=1, null=True),
        ),
    ]