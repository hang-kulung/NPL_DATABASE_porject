from django.urls import path
from . import views
app_name='leaderboard'
urlpatterns=[
    path('api/overall/',views.overall_leaderboard_api,name='overall_leaderboard'),
    path('api/matchday/<int:match_id>/',views.matchday_leaderboard_api,name='matchday_leaderboard')

]