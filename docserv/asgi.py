import os

from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from junk_drawer.sse import EventsRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docserv.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from . import urls_channels  # noqa

application = ProtocolTypeRouter({
    'http': EventsRouter(
        events=AuthMiddlewareStack(
            URLRouter(urls_channels.urlpatterns)
        ),
        web=get_asgi_application(),
    ),
})
