from django.shortcuts import render, redirect
from django.db import connection, IntegrityError
from users.auth import login_required

# Helper function to convert rows to dicts (for easy template use)
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def players_by_team(request, acronym):
    """
    Display all players from a team given its acronym.
    URL example: /players/ABC/
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.player_id, p.player_name, p.role, p.cost, t.team_name, t.acronym
            FROM players p
            JOIN teams t ON p.team_id = t.team_id
            WHERE t.acronym = %s
            ORDER BY p.player_name
        """, [acronym.upper()])  # Convert to uppercase if needed

        players = dictfetchall(cursor)

    return render(request, "players.html", {"players": players, "acronym": acronym})


def add_player(request):
    # Fetch teams for dropdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT team_id, team_name, acronym
            FROM teams
            ORDER BY team_name
        """)
        teams = cursor.fetchall()

    error = None

    if request.method == "POST":
        player_id = request.POST.get("player_id")
        player_name = request.POST.get("player_name")
        role = request.POST.get("role")
        cost = request.POST.get("cost")
        team_id = request.POST.get("team_id")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO players
                    (player_id, player_name, role, cost, team_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, [player_id, player_name, role, cost, team_id])

            return redirect("add_player")

        except IntegrityError:
            error = "Player ID already exists or invalid Team selected."

    return render(request, "add_player.html", {
        "teams": teams,
        "error": error
    })