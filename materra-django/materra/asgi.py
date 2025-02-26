"""
ASGI config for materra project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'materra.settings')

from .routing import router
from channels.routing import ProtocolTypeRouter

application = ProtocolTypeRouter(
            {
                        "http": get_asgi_application(),
                        "websocket": router
            }
)
