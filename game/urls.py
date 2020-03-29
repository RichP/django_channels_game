from django.urls import path

from .views import HomeView, LobbyView, GameView
from .api_views import CurrentUserView, PlayerGameViewSet, AvailableGameViewSet, SingleGameViewSet, GameSquaresViewSet
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('lobby/', LobbyView.as_view(), name='lobby'),
    path('game/<int:pk>/', GameView.as_view(), name='game'),
]

# urls for api - django rest framework
urlpatterns += [
     path('current-user/', CurrentUserView.as_view()),
     path('game-from-id/<int:pk>/', SingleGameViewSet.as_view()),
]

router = DefaultRouter()
router.register('player-games', PlayerGameViewSet, 'player-games')
router.register('available-games', AvailableGameViewSet, 'available_games')
router.register('game-squares', GameSquaresViewSet, 'game_squares')
urlpatterns += router.urls
