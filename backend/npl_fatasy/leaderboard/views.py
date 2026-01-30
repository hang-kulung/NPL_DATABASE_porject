from django.shortcuts import render
import json 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.db import connection


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

@require_http_methods(["GET"])
def overall_leaderboard_api(request):
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                ROW_NUMBER() OVER (ORDER BY SUM(ft.total_points) DESC) AS rank,
                u.user_id AS user_id,
                u.username,
                SUM(ft.total_points) AS total_points
            FROM fantasy_teams ft
            JOIN users u ON ft.user_id = u.user_id
            GROUP BY u.user_id, u.username
            ORDER BY total_points DESC
            LIMIT %s OFFSET %s
        """, [limit, offset])

        leaderboard = dictfetchall(cursor)

    return JsonResponse({
        "leaderboard": leaderboard,
        "limit": limit,
        "offset": offset
    })


@require_http_methods(["GET"])
def matchday_leaderboard_api(request, match_id):
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                ROW_NUMBER() OVER (ORDER BY ft.total_points DESC) AS rank,
                u.user_id AS user_id,
                u.username,
                ft.total_points
            FROM fantasy_teams ft
            JOIN users u ON ft.user_id = u.user_id
            WHERE ft.match_id = %s
            ORDER BY ft.total_points DESC
            LIMIT %s OFFSET %s
        """, [match_id, limit, offset])

        leaderboard = dictfetchall(cursor)

    return JsonResponse({
        "match_id": match_id,
        "leaderboard": leaderboard
    })