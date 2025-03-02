import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from borsa.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borsa_projesi.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP istekleri Django'ya yönlendirilir
    "websocket": AuthMiddlewareStack(  # WebSocket için kimlik doğrulama eklenir
        URLRouter(websocket_urlpatterns)
    ),
})
