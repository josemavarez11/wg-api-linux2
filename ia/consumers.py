import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from django.contrib.auth.models import AnonymousUser
from .views import create_msg_response
from .serializers import MessageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'] and not isinstance(self.scope['user'], AnonymousUser):
            await self.accept()
        else:
            await self.close(code=403)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close(code=403)
            return
        
        if not text_data:
            await self.send(text_data=json.dumps({
                'error': 'Empty message received'
            }))
            return

        message = text_data.strip()
        if not message:
            await self.send(text_data=json.dumps({
                'error': 'No message content'
            }))
            return
        
        try:
            con_response = await database_sync_to_async(create_msg_response)(self.scope['user'].id, message)
            await self.send(text_data=json.dumps(con_response))
        except:
            return await self.send(text_data=json.dumps({
                "error": "Something went wrong trying to generate a response to the message sent."
            }))

        serializer_data = {
            "id_user": self.scope['user'].id,
            "con_message": message,
            "con_response": con_response
        }

        serializer = MessageSerializer(data=serializer_data)

        if await database_sync_to_async(serializer.is_valid)():
            return await database_sync_to_async(serializer.save)()

    @database_sync_to_async
    def save_message(self, user, message):
        Message.objects.create(id_user=user, con_message=message)