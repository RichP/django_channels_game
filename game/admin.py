from django.contrib import admin

# Register your models here.

from .models import Game

class GameAdmin(admin.ModelAdmin):
    fields = ['winner', 'creator', 'opponent', 'cols', 'rows', 'completed', 'current_turn']

admin.site.register(Game, GameAdmin)

