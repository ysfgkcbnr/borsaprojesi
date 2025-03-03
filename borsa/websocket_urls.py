from django.urls import path
from borsa.consumers import ChatConsumer

urlpatterns = [
    path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi(), name="chat_socket"),
]
