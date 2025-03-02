from django.urls import path
from borsa.consumers import ChatConsumer  # WebSocket tüketicinizi içe aktarın

websocket_urlpatterns = [
    path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi(), name="chat_socket"),
]
