from django.urls import path
from .views import match_list, create_fantasy_team, select_players, view_fantasy_team, fantasy_team_results

urlpatterns = [
    path("", match_list, name="match_list"),
    path("create/<int:match_id>/", create_fantasy_team, name="create_fantasy_team"),
    path("select/<int:match_id>/", select_players, name="select_players"),
    path("my-team/<int:match_id>/", view_fantasy_team, name="view_fantasy_team"),
    path("results/<int:match_id>/", fantasy_team_results, name="fantasy_team_results"),
]
