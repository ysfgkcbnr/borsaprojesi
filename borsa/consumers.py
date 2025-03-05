# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import StockAlarm, Notification, Hisse2

class AlarmConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f'alarm_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def check_alarms(self, event):
        alarms = StockAlarm.objects.filter(user=self.user)
        for alarm in alarms:
            hisse = alarm.hisse
            if (alarm.is_above and hisse.fiyat > alarm.threshold) or (not alarm.is_above and hisse.fiyat < alarm.threshold):
                await self.send(text_data=json.dumps({
                    'message': f"{hisse.isim} fiyatı {alarm.threshold} TL eşiğini geçti: {hisse.fiyat} TL",
                }))
                Notification.objects.create(
                    user=self.user,
                    message=f"{hisse.isim} fiyatı {alarm.threshold} TL eşiğini geçti: {hisse.fiyat} TL"
                )
                alarm.delete()  # Alarm bir kez tetiklendiğinde silinsin

    async def receive(self, text_data):
        await self.channel_layer.group_send(self.group_name, {'type': 'check_alarms'})

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
