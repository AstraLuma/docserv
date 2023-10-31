from django.urls import path, include

import pokeberu.consumers

urlpatterns = [
    path('streams/plain', pokeberu.consumers.PlainFeed.as_asgi()),
]
