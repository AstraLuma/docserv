import os

from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docserv.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from . import urls_channels  # noqa

application = ProtocolTypeRouter({
    'http': URLRouter([
        # Cannot use path() if it's immediately handed to middleware.
        # Note that while this falls through correctly, there's probably
        # a performance penalty for running both middleware stacks.
        re_path('^streams/', AuthMiddlewareStack(
            URLRouter(urls_channels.urlpatterns)
        )),
        re_path(r'', get_asgi_application()),
    ]),
})
