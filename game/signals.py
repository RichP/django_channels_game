from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from .serializers import GameSerializer
import json
from .models import Game
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()

@receiver(post_save, sender=Game)
def new_game_handler(**kwargs):
    if kwargs['created']:
        avail_game_list = Game.get_available_games()
        avail_serializer = GameSerializer(avail_game_list, many=True)
        async_to_sync(channel_layer.group_send)("lobby", { "type": "add_game", "text": json.dumps(avail_serializer.data)})
        