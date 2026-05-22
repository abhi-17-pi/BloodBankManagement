"""
ASGI config for BPProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BPProject.settings')

django_asgi_app = get_asgi_application()

from homepage.consumers import CallAlertConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter([
        re_path(r"ws/alerts/$", CallAlertConsumer.as_asgi()),
    ]),
})
