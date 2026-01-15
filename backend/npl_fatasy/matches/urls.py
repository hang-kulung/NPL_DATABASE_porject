from django.urls import path
from .views import match_list, add_match

urlpatterns = [
    path("add/", add_match, name="add_match"),
    path("", match_list, name="match_list"),
]
