from django.views.generic import TemplateView, DetailView
from django.shortcuts import render
from .models import Game
from django.contrib.auth import get_user
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# Create your views here.

class HomeView(TemplateView):
    template_name = 'home.html'

class LobbyView(LoginRequiredMixin, TemplateView):
    template_name = 'lobby.html'
    login_url = 'account_login'
    
    def get_context_data(self, **kwargs):
        context = super(LobbyView, self).get_context_data(**kwargs)
        
        available_games = [{'creator': game.creator.username, 'id': game.pk} for game in Game.get_available_games()]

        player_games = Game.get_games_for_player(self.request.user)
        context['available_games'] = available_games
        context['player_games'] = player_games
        
        return context

class GameView(LoginRequiredMixin, DetailView):
    model = Game
    template_name = 'game.html'
    login_url = 'account_login'

    def dispatch(self, request, *args, **kwargs):
        game = self.get_object()
        usr = request.user
        if game.creator == usr or game.opponent == usr:
            return super(GameView, self).dispatch(request, *args, **kwargs)

        if not game.opponent and not game.completed:
            game.opponent = usr
            game.save()
            return super(GameView, self).dispatch(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Sorry, the selected game is not available.')
            return redirect('/lobby/')
    