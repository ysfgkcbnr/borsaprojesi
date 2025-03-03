import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import borsa.websocket_urls  # WebSocket URL'lerini buraya dahil et

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "borsa_projesi.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(borsa.websocket_urls.urlpatterns),
})
