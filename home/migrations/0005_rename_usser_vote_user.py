# Generated by Django 4.2.2 on 2023-06-14 07:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_vote'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='usser',
            new_name='user',
        ),
    ]
