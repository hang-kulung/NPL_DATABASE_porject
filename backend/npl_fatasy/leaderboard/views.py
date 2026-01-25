from django.shortcuts import render
import json 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.db import connection, IntegrityError


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
            select  
                 user_id,
                 total_points from fantasy_teams
                  where match_id=%s
        """,[match_id])
        teams=dictfetchall(cursor)
        for team in teams:
            user_id=team['user_id']
            points=team['total_points'] or 0
            cursor.execute(""" 
                insert into leaderboard (user_id,match_id,totalpoints)
                values(%s,%s,%s)
                on conflict (user_id,match_id)
                do update set
                           totalpoints=excluded.totalpoints

                """,[user_id,match_id,points])
            cursor.execute("""
                with ranked as (
                           select id, row_number() over(
                                order by totalpoints DESC)
                           as new_rank
                           from leaderboard
                           where match_id=%s)
                           update leaderboard l
                           set rank=r.new_rank
                           from ranked r
                           where l.id=r.id
                           """,[match_id])
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
   
    limit = int(request.GET.get('limit', 100))
    offset = int(request.GET.get('offset', 0))
    
    with connection.cursor() as cursor:
        # Check if leaderboard is empty
        cursor.execute("SELECT COUNT(*) FROM leaderboard")
        count = cursor.fetchone()[0]
        
        # If empty, auto-initialize from fantasy_teams
        if count == 0:
            # Get all users from fantasy_teams
            cursor.execute("SELECT DISTINCT user_id FROM fantasy_teams")
            user_ids = [row[0] for row in cursor.fetchall()]
            
            # Add each user to leaderboard
            for user_id in user_ids:
                update_overall_leaderboard_for_user(user_id)
            
            # Calculate ranks
            update_all_overall_ranks()
        
        # Now fetch and return leaderboard
        cursor.execute("""
            SELECT 
                l.rank,
                l.user_id,
                u.username,
                l.totalpoints
            FROM leaderboard l
            JOIN auth_user u ON l.user_id = u.id
            ORDER BY l.rank ASC
            LIMIT %s OFFSET %s
        """, [limit, offset])
        
        leaderboard = dictfetchall(cursor)
    
    return JsonResponse(leaderboard, safe=False)
@require_http_methods(["GET"])
def matchday_leaderboard_api(request,match_id):
    with connection.cursor() as cursor:
        cursor.execute(""" 
            select count(*) from leaderboard where match_id=%s
        """,[match_id])
        count=cursor.fetchone()[0]

        if count==0:
            update_matchday_leaderboard(match_id)

        cursor.execute("""
                select 
                           l.rank,
                           l.user_id,l.totalpoints as match_points,
                           l.match_id,
                           m.match_date
                           from leaderboard l join matches m on l.match_id=m.match_id
                           where l.match_id=%s
                           order by l.rank ASC
                           """,[match_id])
        leaderboard=dictfetchall(cursor)
    return JsonResponse(leaderboard,safe=False)