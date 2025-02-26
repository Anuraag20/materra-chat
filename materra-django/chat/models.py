from .constants import (
        CONVERSATION_CHANNEL_GROUP,
        CONVERSATION_USER_ID,
        ENQUIRY_NAME_FORMAT,
)
from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

import uuid


layer = get_channel_layer()

class User(AbstractUser):
    is_deleted = models.BooleanField(default = False)
    last_active = models.DateTimeField(null=True, blank=True)
    display_name = models.TextField()

class Enquiry(models.Model):
    TOPICS = (
        ('other', 'other'),
        ('technical', 'technical'),
    )
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_enquiries')
    staff = models.ForeignKey(User, on_delete=models.PROTECT, related_name='assigned_enquiries')
    topic = models.CharField(max_length=15, choices=TOPICS, default=TOPICS[0][0])
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    enquiry = models.ForeignKey(Enquiry, on_delete=models.PROTECT, null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False)

class ConversationMember(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.PROTECT, related_name='members')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='conversations')
    is_admin = models.BooleanField(default=False)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sent')
    conversation = models.ForeignKey(Conversation, on_delete=models.PROTECT, related_name='messages')
    content = models.TextField()
    file = models.FileField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_metadata = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)
        self.conversation.save(update_fields=['last_activity'])
        return self

@receiver(post_save, sender=Conversation, dispatch_uid="conversation_updates")
def conversation_updates(sender, instance: Conversation, created: bool, **kwargs):
    if instance.archived:
        
        group = CONVERSATION_CHANNEL_GROUP.format(instance.id)
        data = {
                'type': 'archive_conversation',
                'data':{
                    'id': str(instance.id)
                }
        }
        async_to_sync(layer.group_send)(group, data)



@receiver(post_save, sender=ConversationMember, dispatch_uid="notify_new_conversation")
def notify_new_conversation(sender, instance: ConversationMember, created: bool, **kwargs):
    if created:
        
        group = CONVERSATION_USER_ID.format(instance.user_id)
        data = {
                'type': 'new_conversation',
                'data':{
                    'id': str(instance.conversation_id),
                    'name': instance.conversation.name,
                    'is_admin': instance.is_admin
                }
        }
        async_to_sync(layer.group_send)(group, data)

    


@receiver(post_save, sender=Enquiry, dispatch_uid="start_support_conversation")
def start_support_conversation(sender, instance: Enquiry, created: bool, **kwargs):
    conversation, created = Conversation.objects.get_or_create(
                        enquiry=instance,
                        archived=False,
                        defaults={
                            'name':ENQUIRY_NAME_FORMAT.format(instance.user.username)
                    })
    if created:
        for user in [instance.user, instance.staff]:
            ConversationMember.objects.create(
                    conversation=conversation,
                    user=user,
                    is_admin=user.is_staff
            )

