from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path("login/", views.admin_login_api, name="admin_login_api"),
    path("session/", views.admin_session_api, name="admin_session_api"),

    # ===========================
    # TEAMS
    # ===========================
    path("teams/", views.list_teams_api, name="list_teams_api"),
    path("teams/add/", views.add_team_api, name="add_team_api"),
    path("teams/<int:team_id>/edit/", views.edit_team_api, name="edit_team_api"),
    path("teams/<int:team_id>/delete/", views.delete_team_api, name="delete_team_api"),

    # ===========================
    # PLAYERS
    # ===========================
    path("players/", views.list_players_api, name="list_players_api"),
    path("players/add/", views.add_player_api, name="add_player_api"),
    path("players/<str:player_id>/delete/", views.delete_player_api, name="delete_player"),
    path("players/<str:player_id>/edit/", views.edit_player_api, name="edit_player"),


    # ===========================
    # MATCHES
    # ===========================
    path("matches/", views.list_matches_api, name="list_matches_api"),
    path("matches/add/", views.add_match_api, name="add_match_api"),
    path("matches/<int:match_id>/edit/", views.edit_match_api, name="edit_match_api"),
    path("matches/<int:match_id>/delete/", views.delete_match_api, name="delete_match_api"),

    # MANAGE MATCH_PLAYERS
    path("match_players/<int:match_id>/", views.match_players_api),
    path("match_players/<int:match_id>/update/", views.update_match_players_api),

    # MANAGE PLAYER STATS
    path("matches/<int:match_id>/stats/", views.manage_player_stats_api),

    # CALCULATE MATCH RESULTS
    path("matches/<int:match_id>/calculate_result/", views.calculate_match_results_api),

]
