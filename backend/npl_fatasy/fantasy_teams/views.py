from django.shortcuts import render, redirect
from django.db import connection
from users.auth import login_required


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@login_required
def view_fantasy_team(request, match_id):

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

    if not players:
        return render(request, "view_team.html", {
            "error": "Fantasy team not created for this match."
        })

    total_cost = sum(p["cost"] for p in players)

    return render(request, "view_team.html", {
        "players": players,
        "total_cost": total_cost,
        "match_id": match_id
    })


@login_required
def fantasy_team_results(request, match_id):

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
                    (CASE 
                        WHEN COALESCE(ps.econ,0) > 0 THEN 10.0 / ps.econ
                        ELSE 0
                     END) +
                    (COALESCE(ps.wickets,0) * 2) +
                    (COALESCE(ps.sixes,0)) +
                    (COALESCE(ps.fours,0) * 0.5) +
                    (COALESCE(ps.catches,0))
                ) AS base_points

            FROM fantasy_team_players ftp
            JOIN players p ON ftp.player_id = p.player_id
            JOIN teams t ON p.team_id = t.team_id
            JOIN match_players mp 
                 ON mp.player_id = p.player_id
                AND mp.match_id = %s
            LEFT JOIN player_stats ps ON ps.mp_id = mp.mp_id
            WHERE ftp.fantasy_team_id = %s
            ORDER BY
                ftp.is_captain DESC,
                ftp.is_vice_captain DESC,
                p.player_name
        """, [match_id, fantasy_team_id])

        players = dictfetchall(cursor)

    if not players:
        return render(request, "result.html", {
            "error": "Fantasy team not created or match not completed."
        })

    total_points = 0
    for p in players:
        if p["is_captain"]:
            p["final_points"] = round(p["base_points"] * 2, 2)
        elif p["is_vice_captain"]:
            p["final_points"] = round(p["base_points"] * 1.5, 2)
        else:
            p["final_points"] = round(p["base_points"], 2)

        total_points += p["final_points"]

    return render(request, "result.html", {
        "players": players,
        "total_points": round(total_points, 2),
        "match_id": match_id
    })



@login_required
def match_list(request):
    """List matches with option to create fantasy team"""

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

    return render(request, "fantasy_match_list.html", {"matches": matches})


@login_required
def create_fantasy_team(request, match_id):
    """Create fantasy team if not exists"""

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

    return redirect("select_players", match_id=match_id)

@login_required
def select_players(request, match_id):

    user_id = request.session["user_id"]
    fantasy_team_id = f"{user_id}_{match_id}"

    # Fetch eligible players
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

    if request.method == "POST":
        selected_players = request.POST.getlist("players")
        captain = request.POST.get("captain")
        vice_captain = request.POST.get("vice_captain")

        # ---------- VALIDATIONS ----------

        # Rule 1: Exactly 7 players
        if len(selected_players) != 7:
            error = "You must select exactly 7 players."

        # Rule 2: Captain & Vice-Captain chosen
        elif not captain or not vice_captain:
            error = "You must choose a Captain and a Vice-Captain."

        # Rule 3: Captain ≠ Vice-Captain
        elif captain == vice_captain:
            error = "Captain and Vice-Captain must be different."

        # Rule 4: Captain & VC must be in selected players
        elif captain not in selected_players or vice_captain not in selected_players:
            error = "Captain and Vice-Captain must be selected players."

        else:
            error = None

        if error:
            return render(request, "select_players.html", {
                "players": players,
                "match_id": match_id,
                "error": error
            })

        # Fetch selected player details
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

        # Rule 5: Max 4 players per team
        if any(count > 4 for count in team_count.values()):
            error = "Maximum 4 players allowed from a single team."

        # Rule 6: Max 3 players per role
        elif any(count > 3 for count in role_count.values()):
            error = "Maximum 3 players allowed per role."

        # Rule 7: Budget limit
        elif total_cost > 60:
            error = f"Total cost exceeded! Current cost: {total_cost}"

        else:
            error = None

        if error:
            return render(request, "select_players.html", {
                "players": players,
                "match_id": match_id,
                "error": error
            })

        # ---------- SAVE SELECTION ----------

        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM fantasy_team_players
                WHERE fantasy_team_id = %s
            """, [fantasy_team_id])

            for pid in selected_players:
                is_captain = (pid == captain)
                is_vice_captain = (pid == vice_captain)

                cursor.execute("""
                    INSERT INTO fantasy_team_players
                    (fantasy_team_id, player_id, is_captain, is_vice_captain)
                    VALUES (%s, %s, %s, %s)
                """, [fantasy_team_id, pid, is_captain, is_vice_captain])

        return redirect("match_list")

    return render(request, "select_players.html", {
        "players": players,
        "match_id": match_id
    })
