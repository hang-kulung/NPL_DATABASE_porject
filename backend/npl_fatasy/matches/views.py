from django.shortcuts import render, redirect
from django.db import connection
from users.auth import login_required

# helper to convert rows → dict
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# LIST MATCHES
def match_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                m.match_id,
                m.match_date,
                t1.team_name AS team1_name,
                t1.acronym AS team1_acronym,
                t2.team_name AS team2_name,
                t2.acronym AS team2_acronym
            FROM matches m
            JOIN teams t1 ON m.team_1 = t1.team_id
            JOIN teams t2 ON m.team_2 = t2.team_id
            ORDER BY m.match_date DESC
        """)
        matches = dictfetchall(cursor)

    return render(request, "match_list.html", {"matches": matches})


def add_match(request):
    # fetch teams for dropdowns
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT team_id, team_name, acronym
            FROM teams
            ORDER BY team_name
        """)
        teams = cursor.fetchall()

    error = None

    if request.method == "POST":
        match_date = request.POST.get("match_date")
        team_1 = request.POST.get("team_1")
        team_2 = request.POST.get("team_2")

        if team_1 == team_2:
            error = "Team 1 and Team 2 cannot be the same."
        else:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO matches (match_date, team_1, team_2)
                    VALUES (%s, %s, %s)
                """, [match_date, team_1, team_2])

            return redirect("match_list")

    return render(request, "add_match.html", {
        "teams": teams,
        "error": error
    })
