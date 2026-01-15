from django.urls import path
from .views import manage_player_stats

urlpatterns = [
    path("<int:match_id>/", manage_player_stats, name="manage_player_stats"),
]
