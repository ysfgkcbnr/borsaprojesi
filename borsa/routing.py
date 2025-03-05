#routing.py
from django.urls import re_path
from . import consumers
from django.urls import path
from .consumers import AlarmConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    path('ws/alarms/', AlarmConsumer.as_asgi(), name='alarm_socket'),
]


