from django.urls import path
from .views import (
    match_list_api,
    create_fantasy_team,
    select_players_api,
    fantasy_team_api,
    fantasy_team_results_api,
    calculate_match_results_api
)

urlpatterns = [
    path("matches/", match_list_api, name="fantasy_matches"),
    path("create/<int:match_id>/", create_fantasy_team, name="fantasy_create"),
    path("select/<int:match_id>/", select_players_api, name="fantasy_select"),
    path("team/<int:match_id>/", fantasy_team_api, name="fantasy_team"),
    path("results/<int:match_id>/", fantasy_team_results_api, name="fantasy_results"),
    path("calculate/<int:match_id>/", calculate_match_results_api, name="calculate_results"),
]