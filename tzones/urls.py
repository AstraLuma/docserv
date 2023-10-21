from django.urls import path

from . import views

urlpatterns = [
    path("<path:zonename>", views.tzdata),
]
