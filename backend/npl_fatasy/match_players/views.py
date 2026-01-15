# Create your views here.
from django.shortcuts import render, redirect
from django.db import connection
import uuid
from users.auth import login_required

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def manage_match_players(request, match_id):
    # 1. Fetch match & teams
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                m.match_id,
                m.match_date,
                t1.team_id AS team1_id,
                t1.team_name AS team1_name,
                t2.team_id AS team2_id,
                t2.team_name AS team2_name
            FROM matches m
            JOIN teams t1 ON m.team_1 = t1.team_id
            JOIN teams t2 ON m.team_2 = t2.team_id
            WHERE m.match_id = %s
        """, [match_id])

        match = cursor.fetchone()

    if not match:
        return render(request, "error.html", {"message": "Match not found"})

    team1_id = match[2]
    team2_id = match[4]

    # 2. Fetch players of both teams + existing selection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.player_id,
                p.player_name,
                t.team_name,
                COALESCE(mp.is_playing, FALSE) AS is_playing
            FROM players p
            JOIN teams t ON p.team_id = t.team_id
            LEFT JOIN match_players mp
                ON mp.player_id = p.player_id
               AND mp.match_id = %s
            WHERE p.team_id IN (%s, %s)
            ORDER BY t.team_name, p.player_name
        """, [match_id, team1_id, team2_id])

        players = dictfetchall(cursor)

    # 3. Save selections
    if request.method == "POST":
        selected_players = request.POST.getlist("playing")

        with connection.cursor() as cursor:
            # Remove old records for this match
            cursor.execute(
                "DELETE FROM match_players WHERE match_id = %s",
                [match_id]
            )

            # Insert fresh records
            for player in players:
                player_id = player["player_id"]
                is_playing = player_id in selected_players

                # ✅ PRIMARY KEY FORMAT: matchid_playerid
                mp_id = f"{match_id}_{player_id}"

                cursor.execute("""
                    INSERT INTO match_players
                    (mp_id, match_id, player_id, is_playing)
                    VALUES (%s, %s, %s, %s)
                """, [mp_id, match_id, player_id, is_playing])

        return redirect("match_list")

    return render(request, "manage_match_players.html", {
        "match": {
            "id": match[0],
            "date": match[1],
            "team1_name": match[3],
            "team2_name": match[5],
        },
        "players": players
    })
