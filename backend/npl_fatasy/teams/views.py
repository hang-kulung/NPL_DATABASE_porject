from django.shortcuts import render
from django.db import connection

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def team_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT team_id, team_name, acronym
            FROM teams
            ORDER BY team_name
        """)
        teams = dictfetchall(cursor)

    return render(request, "teams.html", {"teams": teams})
