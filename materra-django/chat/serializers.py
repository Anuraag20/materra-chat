from .models import Message
from rest_framework.serializers import ModelSerializer

class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ('sender_id', 'conversation_id', 'content',
                    'file', 'created_at', 'is_metadata')
