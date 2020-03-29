from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from .serializers import *
from rest_framework.response import Response
from .models import *
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404


class CurrentUserView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class SingleGameViewSet(RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    def retrieve(self, request, *args, **kwargs):
        game = self.get_object()
        log = game.get_game_log()
        squares = game.get_all_game_squares()

        serializer = GameSerializer(game, many=False)
        square_serializer = GameSquareSerializer(squares, many=True)
        log_serializer = GameLogSerializer(log, many=True)
        return_data = {'game': serializer.data, 'log': log_serializer.data, 'squares':  square_serializer.data }
        return Response(return_data)

class GameSquaresViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        game = get_object_or_404(Game, pk=pk)
        squares = game.get_all_game_squares()
        square_serializer = GameSquareSerializer(squares, many=True)
        Response(square_serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class PlayerGameViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Game.get_games_for_player(self.request.user)
        serializer = GameSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

class AvailableGameViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Game.get_available_games()
        serializer = GameSerializer(queryset, many=True)
        return Response(serializer.data)

class ClaimSquareView(APIView):
    pass




    

