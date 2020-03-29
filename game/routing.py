from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('lobby/', consumers.LobbyConsumer),
    path('game/<int:pk>/', consumers.GameConsumer),
]