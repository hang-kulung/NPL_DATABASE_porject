from django.urls import path
from .views import team_list

urlpatterns = [
    path("list/", team_list, name="team_list"),
]
