import re
import logging
import json
from asgiref.sync import async_to_sync
from .models import Game, GameSquare
from channels.generic.websocket import JsonWebsocketConsumer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LobbyConsumer(JsonWebsocketConsumer):

    http_user = True

    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)("lobby", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("lobby", self.channel_name)

    def receive_json(self, content, **kwargs):
        action = content['action']
        logger.info('LobbyConsumercontentcontentcontent')
        logger.info(content)
        if action == 'create_game':
            # create a new game using the part of the channel name
            user = self.scope['user']
            Game.create_new(user)

    def add_game(self, event):
        Response_ = {
        'Message': "game",
        'Author': "created"} 

        self.send_json({
        'type':'websocket.send',
        'text': json.dumps(Response_)})


class GameConsumer(JsonWebsocketConsumer):
    http_user = True

    def connect(self):
        self.accept()
        id = self.scope["url_route"]["kwargs"]["pk"]
        group_name = "game-{0}".format(id)
        async_to_sync(self.channel_layer.group_add)(group_name, self.channel_name)

    def receive_json(self, content, **kwargs):
        action = content['action']
        #logger.info('contentcontentcontent')
        #logger.info(content)
        logger.info('action')
        logger.info(action)
        if action == 'claim_square':
            square = GameSquare.get_by_id(content['square_id'])
            user = self.scope['user']
            if user.id == square.game.current_turn.id:
                if square.owner == None:
                    square.claim('Selected', user)
                else:
                    logger.info("Illegal Move")
            else:
                logger.info("Incorrect Turn")


        if action == 'chat_text_entered':
            game = Game.get_by_id(content['game_id'])
            user = self.scope['user']
            game.add_log(content['text'], user)
            game.send_game_update()


    def disconnect(self, close_code):
        id = self.scope["url_route"]["kwargs"]["pk"]
        group_name = "game-{0}".format(id)
        async_to_sync(self.channel_layer.group_discard)(group_name, self.channel_name)

    def update_game(self, event):
        Response_ = {
            'game': event
            } 

        self.send_json({
        'type':'websocket.send',
        'object': event['text'] })