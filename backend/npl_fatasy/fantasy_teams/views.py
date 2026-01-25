from django.http import JsonResponse
from django.db import connection
from users.auth import login_required
import json
from leaderboard.views import update_overall_leaderboard_for_user
from leaderboard.views import update_all_overall_ranks
from leaderboard.views import update_matchday_leaderboard
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@login_required
def match_list_api(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                m.match_id,
                m.match_date,
                t1.team_name AS team1,
                t2.team_name AS team2
            FROM matches m
            JOIN teams t1 ON m.team_1 = t1.team_id
            JOIN teams t2 ON m.team_2 = t2.team_id
            ORDER BY m.match_date DESC
        """)
        matches = dictfetchall(cursor)

    return JsonResponse({"matches": matches})


@login_required
def create_fantasy_team(request, match_id):
    user_id = request.session["user_id"]
    fantasy_team_id = f"{user_id}_{match_id}"

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM fantasy_teams
            WHERE fantasy_team_id = %s
        """, [fantasy_team_id])

        exists = cursor.fetchone()

        if not exists:
            cursor.execute("""
                INSERT INTO fantasy_teams
                (fantasy_team_id, user_id, match_id, total_points)
                VALUES (%s, %s, %s, 0)
            """, [fantasy_team_id, user_id, match_id])

            return JsonResponse({"status": "created"})

    return JsonResponse({"status": "exists"})


@login_required
def select_players_api(request, match_id):
    user_id = request.session["user_id"]
    fantasy_team_id = f"{user_id}_{match_id}"

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM fantasy_teams
            WHERE fantasy_team_id = %s
        """, [fantasy_team_id])

        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO fantasy_teams
                (fantasy_team_id, user_id, match_id, total_points)
                VALUES (%s, %s, %s, 0)
            """, [fantasy_team_id, user_id, match_id])

    if request.method == "GET":
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.player_id,
                    p.player_name,
                    p.role,
                    p.cost,
                    t.team_name,
                    t.team_id
                FROM players p
                JOIN teams t ON p.team_id = t.team_id
                WHERE p.team_id IN (
                    SELECT team_1 FROM matches WHERE match_id = %s
                    UNION
                    SELECT team_2 FROM matches WHERE match_id = %s
                )
                ORDER BY t.team_name, p.player_name
            """, [match_id, match_id])

            players = dictfetchall(cursor)

            cursor.execute("""
                SELECT
                    player_id,
                    is_captain,
                    is_vice_captain
                FROM fantasy_team_players
                WHERE fantasy_team_id = %s
            """, [fantasy_team_id])

            rows = dictfetchall(cursor)

        existing_team = None
        if rows:
            existing_team = {
                "players": [r["player_id"] for r in rows],
                "captain": next((r["player_id"] for r in rows if r["is_captain"]), None),
                "vice_captain": next((r["player_id"] for r in rows if r["is_vice_captain"]), None),
            }

        return JsonResponse({
            "players": players,
            "existing_team": existing_team
        })

    if request.method == "POST":
        data = json.loads(request.body)
        selected_players = data.get("players", [])
        captain = data.get("captain")
        vice_captain = data.get("vice_captain")

        if len(selected_players) != 7:
            return JsonResponse({"error": "Select exactly 7 players"}, status=400)

        if not captain or not vice_captain:
            return JsonResponse({"error": "Captain and Vice-Captain required"}, status=400)

        if captain == vice_captain:
            return JsonResponse({"error": "Captain and VC must be different"}, status=400)

        if captain not in selected_players or vice_captain not in selected_players:
            return JsonResponse({"error": "Captain/VC must be selected players"}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT player_id, role, team_id, cost
                FROM players
                WHERE player_id = ANY(%s)
            """, [selected_players])

            selected_data = dictfetchall(cursor)

        team_count = {}
        role_count = {}
        total_cost = 0

        for p in selected_data:
            team_count[p["team_id"]] = team_count.get(p["team_id"], 0) + 1
            role_count[p["role"]] = role_count.get(p["role"], 0) + 1
            total_cost += p["cost"]

        if any(v > 4 for v in team_count.values()):
            return JsonResponse({"error": "Max 4 players per team"}, status=400)

        if any(v > 3 for v in role_count.values()):
            return JsonResponse({"error": "Max 3 players per role"}, status=400)

        if total_cost > 60:
            return JsonResponse({"error": "Budget exceeded"}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM fantasy_team_players
                WHERE fantasy_team_id = %s
            """, [fantasy_team_id])

            for pid in selected_players:
                cursor.execute("""
                    INSERT INTO fantasy_team_players
                    (fantasy_team_id, player_id, is_captain, is_vice_captain)
                    VALUES (%s, %s, %s, %s)
                """, [
                    fantasy_team_id,
                    pid,
                    pid == captain,
                    pid == vice_captain
                ])

        return JsonResponse({"success": True})


@login_required
def fantasy_team_api(request, match_id):
    user_id = request.session["user_id"]
    fantasy_team_id = f"{user_id}_{match_id}"

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.player_name,
                t.team_name,
                p.role,
                p.cost,
                ftp.is_captain,
                ftp.is_vice_captain
            FROM fantasy_team_players ftp
            JOIN players p ON ftp.player_id = p.player_id
            JOIN teams t ON p.team_id = t.team_id
            WHERE ftp.fantasy_team_id = %s
            ORDER BY
                ftp.is_captain DESC,
                ftp.is_vice_captain DESC,
                p.player_name
        """, [fantasy_team_id])

        players = dictfetchall(cursor)
    update_overall_leaderboard_for_user(user_id)
    update_all_overall_ranks()
    update_matchday_leaderboard(match_id)
    return JsonResponse({"players": players})


@login_required
def fantasy_team_results_api(request, match_id):
    user_id = request.session["user_id"]
    fantasy_team_id = f"{user_id}_{match_id}"

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.player_name,
                t.team_name,
                p.role,
                ftp.is_captain,
                ftp.is_vice_captain,
                COALESCE(ps.runs, 0) AS runs,
                COALESCE(ps.run_rate, 0) AS run_rate,
                COALESCE(ps.econ, 0) AS econ,
                COALESCE(ps.wickets, 0) AS wickets,
                COALESCE(ps.sixes, 0) AS sixes,
                COALESCE(ps.fours, 0) AS fours,
                COALESCE(ps.catches, 0) AS catches,
                (
                    (COALESCE(ps.runs,0) / 10.0) +
                    (COALESCE(ps.run_rate,0) / 100.0) +
                    (CASE WHEN COALESCE(ps.econ,0) > 0 THEN 10.0 / ps.econ ELSE 0 END) +
                    (COALESCE(ps.wickets,0) * 2) +
                    (COALESCE(ps.sixes,0)) +
                    (COALESCE(ps.fours,0) * 0.5) +
                    (COALESCE(ps.catches,0))
                ) AS base_points
            FROM fantasy_team_players ftp
            JOIN players p ON ftp.player_id = p.player_id
            JOIN teams t ON p.team_id = t.team_id
            JOIN match_players mp ON mp.player_id = p.player_id AND mp.match_id = %s
            LEFT JOIN player_stats ps ON ps.mp_id = mp.mp_id
            WHERE ftp.fantasy_team_id = %s
            ORDER BY ftp.is_captain DESC, ftp.is_vice_captain DESC, p.player_name
        """, [match_id, fantasy_team_id])

        players = dictfetchall(cursor)

    total_points = 0
    for p in players:
        if p["is_captain"]:
            p["final_points"] = round(p["base_points"] * 2, 2)
        elif p["is_vice_captain"]:
            p["final_points"] = round(p["base_points"] * 1.5, 2)
        else:
            p["final_points"] = round(p["base_points"], 2)

        total_points += p["final_points"]

    return JsonResponse({
        "players": players,
        "total_points": round(total_points, 2)
    })
