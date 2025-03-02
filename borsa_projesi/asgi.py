import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from borsa.consumers import ChatConsumer
from borsa.websocket_urls import websocket_urlpatterns  # websocket_urlpatterns import edilmeli
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borsa.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/", ChatConsumer.as_asgi()),  # WebSocket yolunu buraya ekleyin
        ])
    ),
})