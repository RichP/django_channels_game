from django.db import models
from django.contrib.auth import get_user_model
import json
from datetime import datetime
# Create your models here.

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game(models.Model):
    creator = models.ForeignKey(
        get_user_model(),
        related_name='creator',
        on_delete=models.CASCADE
    )
    opponent = models.ForeignKey(
        get_user_model(),
        related_name='opponent',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    winner = models.ForeignKey(
        get_user_model(),
        related_name='winner',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    cols = models.IntegerField(default=6)
    rows = models.IntegerField(default=6)
    current_turn = models.ForeignKey(
        get_user_model(),
        related_name='current',
        on_delete=models.CASCADE
    )

    completed = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Game #{0}'.format(self.pk)
    
    @staticmethod
    def get_available_games():
        return Game.objects.filter(opponent=None, completed=None)

    @staticmethod
    def created_count(user):
        return Game.objects.filter(creater=user).count()

    @staticmethod
    def get_games_for_player(user):
        from django.db.models import Q
        return Game.objects.filter(Q(opponent=user) | Q(creator=user))

    @staticmethod
    def get_by_id(id):
        try:
            return Game.objects.get(pk=id)
        except Game.DoesNotExist:
            pass

    @staticmethod
    def create_new(user):
        new_game = Game(creator=user, current_turn=user)
        new_game.save()

        for row in range(new_game.rows):
            for col in range(new_game.cols):
                new_square = GameSquare(
                    game=new_game,
                    row=row,
                    col=col
                )
                new_square.save()
        new_game.add_log('Game created by {0}'.format(new_game.creator.username))

        return new_game
    
    def add_log(self, text, user=None):
        entry = GameLog(game=self, text=text, player=user).save()
        return entry

    def get_all_game_squares(self):
        return GameSquare.objects.filter(game=self)

    def get_game_square(row, col):
        try:
            return GameSquare.objects.get(game=self, cols=col, rows=row)
        except GameSquare.DoesNotExist:
            return None

    def get_square_by_coords(self, coords):
        try:
            square = GameSquare.objects.get(row=coords[1],
            col=coords[0],
            game=self)
            return square
        except GameSquare.DoesNotExist:
            return None
        
    def get_game_log(self):
        return GameLog.objects.filter(game=self)

    def send_game_update(self):
        from .serializers import GameSquareSerializer, GameSerializer, GameLogSerializer
        squares = self.get_all_game_squares()
        square_serializer = GameSquareSerializer(squares, many=True)
        log = self.get_game_log()
        log_serializer = GameLogSerializer(log, many=True)
        game_serializer = GameSerializer(self)

        message = {'game': game_serializer.data, 
        'log': log_serializer.data, 
        'squares': square_serializer.data}
        game_group = 'game-{0}'.format(self.id)
        async_to_sync(channel_layer.group_send)(game_group, { "type": "update_game", "text": message})

    def next_player_turn(self):
        self.current_turn = self.creator if self.current_turn != self.creator else self.opponent
        self.save()


    def mark_complete(self, winner):
        self.winner = winner
        self.completed = datetime.now()
        self.save()


class GameSquare(models.Model):
    STATUS_TYPES = (
        ('FREE', 'FREE'),
        ('Selected', 'Selected'),
        ('Surrounding', 'Surrounding')
    )

    game = models.ForeignKey(Game,
        on_delete=models.CASCADE)
    owner = models.ForeignKey(get_user_model(), null=True, blank=True,
        on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_TYPES, max_length=25, default='FREE')

    row = models.IntegerField()
    col = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0} - ({1}, {2})'.format(self.game, self.col, self.row)

    @staticmethod
    def get_by_id(id):
        try:
            return GameSquare.objects.get(pk=id)
        except GameSquare.DoesNotExist:
            return None

    def get_surrounding(self):
        # http://stackoverflow.com/questions/2373306/pythonic-and-efficient-way-of-finding-adjacent-cells-in-grid
        ajecency_matrix = [(i, j) for i in (-1, 0, 1)
                           for j in (-1, 0, 1) if not (i == j == 0)]

        results = []
        for dx, dy in ajecency_matrix:
            if 0 <= (self.col + dy) < self.game.cols and 0 <= self.row + dx < self.game.rows:
                results.append((self.col + dy, self.row + dx))
        return results

    def claim(self, status_type, user):
        logger.info('status_type')
        logger.info(status_type)

        self.owner = user
        self.status = status_type

        self.save(update_fields=['status', 'owner'])

        surrounding = self.get_surrounding()

        for coords in surrounding:
            square = self.game.get_square_by_coords(coords)

            if square and square.status == 'FREE':
                square.status = 'Surrounding'
                square.owner = user
                square.save() 

        self.game.add_log('Square claimed at ({0}, {1}) by {2}'.format(self.col, self.row, self.owner.username))

        if self.game.get_all_game_squares().filter(status='FREE'):
            self.game.next_player_turn()
        else:
            self.game.mark_complete(winner=user)
        self.game.send_game_update()


class GameLog(models.Model):
    game = models.ForeignKey(Game,
        on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    player = models.ForeignKey(get_user_model(), null=True, blank=True,
        on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Game #{0} Log'.format(self.game.id)

       
