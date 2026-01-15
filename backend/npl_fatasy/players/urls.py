from django.urls import path
from .views import players_by_team, add_player

urlpatterns = [
    path("add/", add_player, name="add_player"),
    path("<str:acronym>/", players_by_team, name="players_by_team"),
]