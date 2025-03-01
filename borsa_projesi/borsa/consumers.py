# borsa/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # WebSocket bağlantısını kabul et
        self.room_group_name = 'chat_room'  # Odaların adları buraya yazılır

        # Odadaki kullanıcıları abone et
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Bağlantı kurulduğunda WebSocket'i aç
        await self.accept()

    async def disconnect(self, close_code):
        # WebSocket bağlantısı kapatıldığında grubun çıkışı
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # WebSocket'ten gelen mesajı al
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Gruba mesaj gönder
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # Grubun mesajını WebSocket'teki alıcıya gönder
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
