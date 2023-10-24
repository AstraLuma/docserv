from django.urls import path, include

import pokeberu.consumers

urlpatterns = [
    path('plain', pokeberu.consumers.PlainFeed.as_asgi()),
]
