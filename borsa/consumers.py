# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chatroom'
        self.room_group_name = f'chat_{self.room_name}'

        # Kanal grubuna katıl
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Kanal grubundan çık
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Mesaj alındığında bu fonksiyon çalışır
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Kanal grubuna mesaj gönder
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Mesaj gönderildiğinde bu fonksiyon çalışır
    async def chat_message(self, event):
        message = event['message']

        # WebSocket'e mesaj gönder
        await self.send(text_data=json.dumps({
            'message': message
        }))
