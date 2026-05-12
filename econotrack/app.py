from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "econotrack_secret"

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE
@app.route("/")
def index():
    return "EconoTrack Home Page"


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        return f"Logged in as {email}"

    return "Login Page"


# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")

        return f"Registered {username}"

    return "Register Page"


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    news = conn.execute("SELECT * FROM news").fetchall()

    conn.close()

    return render_template("dashboard.html", news=news)


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)