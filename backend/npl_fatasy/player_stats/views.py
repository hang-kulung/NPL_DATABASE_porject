from django.shortcuts import render, redirect
from django.db import connection
from users.auth import login_required


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def manage_player_stats(request, match_id):
    """
    Add/Edit stats for all playing players in a match
    """

    # 1. Fetch all playing players in the match
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

    # 2. Save stats
    if request.method == "POST":
        with connection.cursor() as cursor:
            for p in players:
                mp_id = p["mp_id"]
                stat_id = f"{mp_id}_STAT"

                run_rate = request.POST.get(f"run_rate_{mp_id}", 0)
                econ = request.POST.get(f"econ_{mp_id}", 0)
                wickets = request.POST.get(f"wickets_{mp_id}", 0)
                sixes = request.POST.get(f"sixes_{mp_id}", 0)
                fours = request.POST.get(f"fours_{mp_id}", 0)
                catches = request.POST.get(f"catches_{mp_id}", 0)
                runs = request.POST.get(f"runs_{mp_id}", 0)

                # Check if stats already exist
                cursor.execute("""
                    SELECT 1 FROM player_stats WHERE mp_id = %s
                """, [mp_id])

                exists = cursor.fetchone()

                if exists:
                    cursor.execute("""
                        UPDATE player_stats
                        SET run_rate=%s, econ=%s, wickets=%s,
                            sixes=%s, fours=%s, catches=%s, runs=%s
                        WHERE mp_id=%s
                    """, [
                        run_rate, econ, wickets,
                        sixes, fours, catches, runs, mp_id
                    ])
                else:
                    cursor.execute("""
                        INSERT INTO player_stats
                        (stat_id, mp_id, run_rate, econ, wickets, sixes, fours, catches, runs)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        stat_id, mp_id, run_rate, econ,
                        wickets, sixes, fours, catches, runs
                    ])

        return redirect("match_list")

    return render(request, "manage_stats.html", {
        "players": players,
        "match_id": match_id
    })
