from .constants import CONVERSATION_CHANNEL_GROUP
from .models import (
    Conversation,
    ConversationMember,
    Enquiry,
    Message
)

from .serializers import  (
    MessageSerializer        
)

from .utils import (
    has_conversation_access,
    get_available_staff
)

from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render
from django.utils import timezone


from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

User = get_user_model()
layer = get_channel_layer()

def index(request):
    return render(request, 'chat/index.html')

@login_required
def room(request):
    return render(request, 'chat/room.html')

class EnquiryViewset(ViewSet):
    def create_enquiry(self, request):
        Enquiry.objects.get_or_create(
                user_id=request.data.get('user_id'),
                is_active=True,
                defaults={
                    'staff': get_available_staff(),
                    'topic': request.data.get('topic', 'other'),
                    'description': request.data.get('description')
            })

        return Response(status=status.HTTP_201_CREATED)

    def resolve_enquiry(self, request, enquiry_id: int):
        ...


class ConversationViewset(ViewSet):
    permission_classes = [IsAuthenticated]

    def create_conversation(self, request):
        users = request.data.get('users')        
        conversation_name = request.data.get('conversation_name')

        conversation = Conversation.objects.create(name=conversation_name)
        users = User.objects.filter(username__in=users).only('id')

        for user in users:
            ConversationMember.objects.create(
                    user_id=user.id, 
                    conversation_id=conversation.id,
                    is_admin=user==request.user
            )
        return Response(status=status.HTTP_201_CREATED)
      
    @has_conversation_access()
    def get_messages(self, request, conversation_id):
        filters = {'conversation_id': conversation_id}

        if before:=request.query_params.get('before'):
            #TODO: parse the time string
            filters['created_at__lte'] = timezone.make_aware(before)
        if after:=request.query_params.get('after'):
            filters['created_at__gte'] = timezone.make_aware(after)

        messages = Message.objects.filter(**filters)        
        data = MessageSerializer(messages, many=True).data

        return Response(data=data, status=status.HTTP_200_OK)

    def get_conversations(self, request):
        #TODO: Properly paginate this
        conversations = ConversationMember.objects.filter(
                    user_id=request.user.id,
                    conversation__archived=False,
                ).only('conversation_id', 'is_admin'). \
                annotate(
                    name=F('conversation__name'), 
                    last_activity=F('conversation__last_activity')
                ). \
                order_by('-last_activity')
        data = []
        for conversation in conversations:
            data.append({
                'id': conversation.conversation_id,
                'name': conversation.name,
                'is_admin': conversation.is_admin
            })
        return Response(data=data, status=status.HTTP_200_OK)

    @has_conversation_access(requires_admin=False)
    def get_members(self, request, conversation_id):
        members = ConversationMember.objects.filter(
                    conversation_id=conversation_id
                ).only('user_id').annotate(
                    name=F('user__display_name')
                ).values('user_id', 'name')
        data = {}
        for member in members:
            data[int(member['user_id'])] = member['name']
        return Response(data, status=status.HTTP_200_OK)
    
    @has_conversation_access()
    def upload_file(self, request, conversation_id):
        message = Message.objects.create(
            sender_id=request.user.id,
            conversation_id=conversation_id,
            content=request.data.get('message'),
            file=request.data.get('file')
        )
        group = CONVERSATION_CHANNEL_GROUP.format(conversation_id)
        data = {
                'type': 'broadcast_message',
                'data': MessageSerializer(message).data
        }
        async_to_sync(layer.group_send)(group, data)
        return Response(status=status.HTTP_201_CREATED)

    @has_conversation_access(requires_admin=True)
    def archive_conversation(self, request, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id)
        conversation.archived = True
        if conversation.enquiry_id:
            enquiry = conversation.enquiry
            enquiry.is_active = False
            enquiry.save()

        conversation.save()

        return Response(status=status.HTTP_200_OK)
