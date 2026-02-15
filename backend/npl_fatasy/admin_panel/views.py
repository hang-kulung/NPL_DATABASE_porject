from django.http import JsonResponse
from django.db import connection, IntegrityError
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.timezone import localdate
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from leaderboard.views import update_all_overall_ranks, update_matchday_leaderboard, update_overall_leaderboard_for_user


@login_required
def admin_session_api(request):
    if request.user.is_superuser:
        return JsonResponse({"authenticated": True})
    return JsonResponse({"authenticated": False}, status=403)


def admin_login_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if user and user.is_superuser:
            login(request, user)
            return JsonResponse({"status": "ok"})

        return JsonResponse({"error": "Invalid admin credentials"}, status=401)

    except Exception:
        return JsonResponse({"error": "Invalid request"}, status=400)
    

# ===========================
# HELPER
# ===========================
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ===========================
# TEAMS CRUD
# ===========================
@login_required
def list_teams_api(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT team_id, team_name, acronym FROM teams ORDER BY team_name")
        teams = dictfetchall(cursor)
    return JsonResponse({"teams": teams})


@csrf_exempt
@login_required
def add_team_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    team_name = data.get("team_name", "").strip()
    acronym = data.get("acronym", "").strip()

    if not team_name or not acronym:
        return JsonResponse({"error": "Team name and acronym are required"}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(team_id), 0) + 1 FROM teams")
            new_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO teams (team_id, team_name, acronym) VALUES (%s, %s, %s)",
                [new_id, team_name, acronym],
            )
        return JsonResponse({"status": "created"})
    except IntegrityError as e:
        return JsonResponse({"error": str(e)}, status=400)



@csrf_exempt
@login_required
def edit_team_api(request, team_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT required"}, status=405)
    try:
        data = json.loads(request.body)
        team_name = data.get("team_name")
        acronym = data.get("acronym")

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE teams SET team_name=%s, acronym=%s WHERE team_id=%s",
                [team_name, acronym, team_id],
            )
        return JsonResponse({"status": "updated"})
    except IntegrityError:
        return JsonResponse({"error": "Update failed"}, status=400)


@csrf_exempt
@login_required
def delete_team_api(request, team_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE required"}, status=405)
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM players WHERE team_id=%s", [team_id])
        cursor.execute("""
            DELETE FROM matches
            WHERE team_1=%s OR team_2=%s
        """, [team_id, team_id])
        cursor.execute("DELETE FROM teams WHERE team_id=%s", [team_id])
    return JsonResponse({"status": "deleted"})


###########################
# Players CRUD
###########################

@login_required
@require_http_methods(["GET"])
def list_players_api(request):
    """
    Return list of players with optional filters:
    ?name=...&role=...&team_id=...&max_cost=...
    """
    filters = []
    params = []

    id = request.GET.get("player_id")
    name = request.GET.get("name")
    role = request.GET.get("role")
    team_id = request.GET.get("team_id")
    max_cost = request.GET.get("max_cost")

    if id:
        filters.append("p.player_id ILIKE %s")
        params.append(f"%{id}%")  # case-insensitive match

    if name:
        filters.append("p.player_name ILIKE %s")
        params.append(f"%{name}%")  # case-insensitive match

    if role:
        filters.append("p.role = %s")
        params.append(role)

    if team_id:
        filters.append("p.team_id = %s")
        params.append(team_id)

    if max_cost:
        filters.append("p.cost <= %s")
        params.append(max_cost)

    where_clause = " AND ".join(filters)
    if where_clause:
        where_clause = "WHERE " + where_clause

    query = f"""
        SELECT 
            p.player_id,
            p.player_name,
            p.role,
            p.cost,
            p.team_id,
            t.team_name
        FROM players p
        JOIN teams t ON p.team_id = t.team_id
        {where_clause}
        ORDER BY p.player_name
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        players = dictfetchall(cursor)

    return JsonResponse({"players": players})


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def add_player_api(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        player_id = data["player_id"]
        player_name = data["player_name"]
        role = data["role"]
        cost = float(data["cost"])
        team_id = int(data["team_id"])
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO players
            (player_id, player_name, role, cost, team_id)
            VALUES (%s, %s, %s, %s, %s)
        """, [player_id, player_name, role, cost, team_id])

    return JsonResponse({"status": "created"})

@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def edit_player_api(request, player_id):

    try:
        data = json.loads(request.body.decode())
        player_name = data["player_name"]
        role = data["role"]
        cost = int(data["cost"])
        team_id = int(data["team_id"])
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE players
            SET player_name=%s,
                role=%s,
                cost=%s,
                team_id=%s
            WHERE player_id=%s
        """, [player_name, role, cost, team_id, player_id])

        if cursor.rowcount == 0:
            return JsonResponse({"error": "Player not found"}, status=404)

    return JsonResponse({"status": "updated"})


@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_player_api(request, player_id):

    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM players WHERE player_id=%s",
            [player_id]
        )

        if cursor.rowcount == 0:
            return JsonResponse(
                {"error": "Player not found"},
                status=404
            )

    return JsonResponse({"status": "deleted"})

# ===========================
# MATCHES CRUD
# ===========================
@login_required
@require_http_methods(["GET"])
def list_matches_api(request):

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
            ORDER BY m.match_date ASC
        """)
        rows = dictfetchall(cursor)

    today = localdate()

    matches = []
    for r in rows:
        matches.append({
            "id": r["match_id"],
            "teams": f'{r["team1"]} vs {r["team2"]}',
            "match_date": r["match_date"].strftime("%Y-%m-%d"),
            "status": "Upcoming" if r["match_date"] >= today else "Completed",
            "team_1": r["team1"], 
            "team_2": r["team2"]
        })

    return JsonResponse({"matches": matches})


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def add_match_api(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        match_date = data["match_date"]
        team_1 = int(data["team_1"])
        team_2 = int(data["team_2"])
    except Exception:
        return JsonResponse({"error": "Invalid JSON or fields"}, status=400)

    if team_1 == team_2:
        return JsonResponse({"error": "Teams cannot be same"}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO matches (match_date, team_1, team_2)
                VALUES (%s, %s, %s)
                RETURNING match_id
            """, [match_date, team_1, team_2])

            match_id = cursor.fetchone()[0]

        return JsonResponse({
            "status": "created",
            "match_id": match_id
        })

    except IntegrityError:
        return JsonResponse({"error": "Insert failed"}, status=400)

@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def edit_match_api(request, match_id):

    try:
        data = json.loads(request.body)
        match_date = data["match_date"]
        team_1 = int(data["team_1"])
        team_2 = int(data["team_2"])
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if team_1 == team_2:
        return JsonResponse({"error": "Teams cannot be same"}, status=400)

    
    with connection.cursor() as cursor:

        # check exists
        cursor.execute(
            "SELECT 1 FROM matches WHERE match_id=%s",
            [match_id]
        )
        if not cursor.fetchone():
            return JsonResponse({"error": "Match not found"}, status=404)

        cursor.execute(
            "DELETE FROM matches WHERE match_id=%s",
            [match_id]
        )

        # insert new with SAME ID
        cursor.execute("""
            INSERT INTO matches
            (match_id, match_date, team_1, team_2)
            VALUES (%s, %s, %s, %s)
        """, [match_id, match_date, team_1, team_2])

    return JsonResponse({"status": "updated"})

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_match_api(request, match_id):

    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM matches WHERE match_id=%s",
            [match_id]
        )

        if cursor.rowcount == 0:
            return JsonResponse(
                {"error": "Match not found"},
                status=404
            )

    return JsonResponse({"status": "deleted"})



################
# MTACH PLAYERS
################
@login_required
def match_players_api(request, match_id):
    """
    GET: fetch all players for a match with playing status
    POST: update playing status for players of the match
    """
    if request.method == "GET":
        with connection.cursor() as cursor:
            # Fetch match info
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
            return JsonResponse({"error": "Match not found"}, status=404)

        team1_id, team2_id = match[2], match[4]

        # Fetch players for both teams + playing status
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

        return JsonResponse({
            "match": {
                "id": match[0],
                "date": str(match[1]),
                "team1_id": match[2],
                "team1_name": match[3],
                "team2_id": match[4],
                "team2_name": match[5],
            },
            "players": players
        })


@csrf_exempt
@login_required
def update_match_players_api(request, match_id):
    """
    POST: update playing status
    Expect JSON: { "playing": [player_id1, player_id2, ...] }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        selected_players = data.get("playing_ids", [])
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Fetch players of match
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT player_id
            FROM players
            WHERE team_id IN (
                SELECT team_1 FROM matches WHERE match_id=%s
                UNION
                SELECT team_2 FROM matches WHERE match_id=%s
            )
        """, [match_id, match_id])
        valid_players = [row[0] for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        # Delete old entries
        cursor.execute("DELETE FROM match_players WHERE match_id=%s", [match_id])

        # Insert updated entries
        for pid in valid_players:
            is_playing = pid in selected_players
            mp_id = f"{match_id}_{pid}"
            cursor.execute("""
                INSERT INTO match_players (mp_id, match_id, player_id, is_playing)
                VALUES (%s, %s, %s, %s)
            """, [mp_id, match_id, pid, is_playing])

    return JsonResponse({"status": "updated", "selected_players": selected_players})


#########################
# MATCH_PLAYERS STATS
##########################

@csrf_exempt
@login_required
@require_http_methods(["GET", "POST"])
def manage_player_stats_api(request, match_id):

    # -------------------------
    # GET — fetch players + stats
    # -------------------------
    if request.method == "GET":
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    mp.mp_id,
                    p.player_name,
                    t.team_name,
                    COALESCE(ps.run_rate, 0) AS run_rate,
                    COALESCE(ps.econ, 0) AS econ,
                    COALESCE(ps.wickets, 0) AS wickets,
                    COALESCE(ps.sixes, 0) AS sixes,
                    COALESCE(ps.fours, 0) AS fours,
                    COALESCE(ps.catches, 0) AS catches,
                    COALESCE(ps.runs, 0) AS runs
                FROM match_players mp
                JOIN players p ON mp.player_id = p.player_id
                JOIN teams t ON p.team_id = t.team_id
                LEFT JOIN player_stats ps ON mp.mp_id = ps.mp_id
                WHERE mp.match_id = %s
                  AND mp.is_playing = TRUE
                ORDER BY t.team_name, p.player_name
            """, [match_id])

            players = dictfetchall(cursor)

        return JsonResponse({"players": players})

    # -------------------------
    # POST — save stats
    # -------------------------
    data = json.loads(request.body)

    with connection.cursor() as cursor:
        for p in data["players"]:
            mp_id = p["mp_id"]
            stat_id = f"{mp_id}_STAT"

            cursor.execute(
                "SELECT 1 FROM player_stats WHERE mp_id=%s",
                [mp_id]
            )

            if cursor.fetchone():
                cursor.execute("""
                    UPDATE player_stats SET
                        run_rate=%s,
                        econ=%s,
                        wickets=%s,
                        sixes=%s,
                        fours=%s,
                        catches=%s,
                        runs=%s
                    WHERE mp_id=%s
                """, [
                    p["run_rate"], p["econ"], p["wickets"],
                    p["sixes"], p["fours"], p["catches"],
                    p["runs"], mp_id
                ])
            else:
                cursor.execute("""
                    INSERT INTO player_stats
                    (stat_id, mp_id, run_rate, econ, wickets,
                     sixes, fours, catches, runs)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [
                    stat_id, mp_id,
                    p["run_rate"], p["econ"], p["wickets"],
                    p["sixes"], p["fours"], p["catches"], p["runs"]
                ])

    return JsonResponse({"status": "saved"})


##############
# MATCH RESULT CAlCULATE
###################

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def calculate_match_results_api(request, match_id):
    """
    Calculate & store fantasy points for ALL users for a match
    """

    with connection.cursor() as cursor:
        # Get all fantasy teams for this match
        cursor.execute("""
            SELECT fantasy_team_id, user_id
            FROM fantasy_teams
            WHERE match_id = %s
        """, [match_id])

        teams = dictfetchall(cursor)

    for team in teams:
        fantasy_team_id = team["fantasy_team_id"]
        user_id = team["user_id"]

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    ftp.is_captain,
                    ftp.is_vice_captain,
                    (
                        (COALESCE(ps.runs,0) / 10.0) +
                        (COALESCE(ps.run_rate,0) / 100.0) +
                        (CASE 
                            WHEN COALESCE(ps.econ,0) > 0 
                            THEN 10.0 / ps.econ 
                            ELSE 0 
                        END) +
                        (COALESCE(ps.wickets,0) * 2) +
                        (COALESCE(ps.sixes,0)) +
                        (COALESCE(ps.fours,0) * 0.5) +
                        (COALESCE(ps.catches,0))
                    ) AS base_points
                FROM fantasy_team_players ftp
                JOIN match_players mp 
                    ON mp.player_id = ftp.player_id
                   AND mp.match_id = %s
                LEFT JOIN player_stats ps 
                    ON ps.mp_id = mp.mp_id
                WHERE ftp.fantasy_team_id = %s
            """, [match_id, fantasy_team_id])

            players = dictfetchall(cursor)

        total_points = 0

        for p in players:
            if p["is_captain"]:
                total_points += p["base_points"] * 2
            elif p["is_vice_captain"]:
                total_points += p["base_points"] * 1.5
            else:
                total_points += p["base_points"]

        total_points = round(total_points, 2)

        # 🔥 Store result
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE fantasy_teams
                SET total_points = %s
                WHERE fantasy_team_id = %s
            """, [total_points, fantasy_team_id])

        # 🔥 Update leaderboards
        update_overall_leaderboard_for_user(user_id)

    update_all_overall_ranks()
    update_matchday_leaderboard(match_id)

    return JsonResponse({
        "status": "success",
        "match_id": match_id,
        "teams_processed": len(teams)
    })