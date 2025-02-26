from .constants import (
        CONVERSATION_CHANNEL_GROUP,
        CONVERSATION_USER_ID
)
from .models import (
    ConversationMember,
    Message
)
from .serializers import MessageSerializer
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

import json

class RoomConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):      
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        # This is done for sending user-specific notifications
        # Do something else in prod!
        
        await self.channel_layer.group_add(
                CONVERSATION_USER_ID.format(self.user_id), self.channel_name
            )

        async for cid in self.get_chat_rooms():
            await self.channel_layer.group_add(
                CONVERSATION_CHANNEL_GROUP.format(cid), self.channel_name
            )
        await self.accept()
    
    def get_chat_rooms(self):
        return ConversationMember.objects.filter(user_id=self.user_id).values_list('conversation_id', flat=True)
    
    async def new_conversation(self, event):
        await self.channel_layer.group_add(
                CONVERSATION_CHANNEL_GROUP.format(event['data']['id']), self.channel_name
            )
        await self.send(text_data=json.dumps(event))
    
    #Ideally change the handling so code does not get repeated
    async def archive_conversation(self, event):
        await self.send(text_data=json.dumps(event))

    async def broadcast_message(self, event):
        await self.send(text_data=json.dumps(event))
        
    async def __new_message(self, data):
        message = Message(
                    sender_id=self.user_id,
                    conversation_id=data['conversation'],
                    content=data['message']
                )
        await message.asave()
        serializer = await sync_to_async(MessageSerializer)(message)

        await self.channel_layer.group_send(
            CONVERSATION_CHANNEL_GROUP.format(data['conversation']),
            {
                'type': 'broadcast_message',
                'data': serializer.data
            }
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']

        match text_data_json['type']:
            case 'new_message':
                await self.__new_message(data)
            case _:
                ...
                #TODO: Implement some default behaviour
