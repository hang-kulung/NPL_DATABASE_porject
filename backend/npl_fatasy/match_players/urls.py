from django.urls import path
from .views import manage_match_players

urlpatterns = [
    path("<int:match_id>/", manage_match_players, name="manage_match_players"),
]
