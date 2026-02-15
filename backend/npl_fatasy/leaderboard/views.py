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


def dictfetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None

def update_matchday_leaderboard(match_id):
    with connection.cursor() as cursor:
        cursor.execute(""" 
            SELECT user_id, total_points
            FROM fantasy_teams
            WHERE match_id=%s
        """,[match_id])

        teams = dictfetchall(cursor)

        for team in teams:
            cursor.execute(""" 
                INSERT INTO leaderboard (user_id, match_id, totalpoints)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, match_id)
                DO UPDATE SET totalpoints = EXCLUDED.totalpoints
            """, [team['user_id'], match_id, team['total_points'] or 0])

        # Rank AFTER all inserts
        cursor.execute("""
            WITH ranked AS (
                SELECT id,
                       ROW_NUMBER() OVER (ORDER BY totalpoints DESC) AS new_rank
                FROM leaderboard
                WHERE match_id=%s
            )
            UPDATE leaderboard l
            SET rank = r.new_rank
            FROM ranked r
            WHERE l.id = r.id
        """, [match_id])

            
def update_overall_leaderboard_for_user(user_id):
    """
    Update leaderboard for a user by summing ALL their fantasy team points
    """
    with connection.cursor() as cursor:
        # Sum all fantasy teams for this user
        cursor.execute("""
            SELECT 
                SUM(total_points) as total_points
            FROM fantasy_teams
            WHERE user_id = %s
        """, [user_id])
        
        stats = dictfetchone(cursor)
        
        if not stats:
            return
        
        # Insert or update leaderboard
        cursor.execute("""
            INSERT INTO leaderboard (user_id,match_id, totalpoints)
            VALUES (%s,NULL,%s)
            ON CONFLICT (user_id,match_id)
            DO UPDATE SET 
                totalpoints = EXCLUDED.totalpoints
        """, [
            user_id,
            stats['total_points'] or 0
        ])


def update_all_overall_ranks():
    """
    Update ranks for all users in the leaderboard
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH ranked AS (
                SELECT 
                    id,
                    ROW_NUMBER() OVER (
                        ORDER BY totalpoints DESC
                    ) as new_rank
                FROM leaderboard
                where match_id is null
            )
            UPDATE leaderboard l
            SET rank = r.new_rank
            FROM ranked r
            WHERE l.id = r.id
        """)


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
