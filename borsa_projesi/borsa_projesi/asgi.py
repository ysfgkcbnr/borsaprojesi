"""
ASGI config for borsa_projesi project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borsa_projesi.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # WebSocket ve diğer protokoller için routing ekleyebilirsiniz
})
