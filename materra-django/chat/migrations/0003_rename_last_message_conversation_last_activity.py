# Generated by Django 5.1.6 on 2025-02-25 03:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_remove_conversationmember_is_active_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='conversation',
            old_name='last_message',
            new_name='last_activity',
        ),
    ]
