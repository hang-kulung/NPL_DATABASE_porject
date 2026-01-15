from django.shortcuts import render, redirect
from django.db import connection, IntegrityError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

def register(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        hashed_password = make_password(password)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, password)
                    VALUES (%s, %s)
                """, [username, hashed_password])

            return redirect("login")

        except IntegrityError:
            error = "Username already exists"

    return render(request, "register.html", {"error": error})


def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, password
                FROM users
                WHERE username = %s
            """, [username])

            user = cursor.fetchone()

        if user and check_password(password, user[1]):
            request.session["user_id"] = user[0]
            request.session["username"] = username
            return redirect("team_list")
        else:
            error = "Invalid credentials"

    return render(request, "login.html", {"error": error})

def logout_view(request):
    request.session.flush()
    return redirect("login")


