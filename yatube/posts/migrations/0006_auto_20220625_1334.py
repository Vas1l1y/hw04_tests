# Generated by Django 2.2.19 on 2022-06-25 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20220625_1305'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='descprition',
            new_name='description',
        ),
    ]
