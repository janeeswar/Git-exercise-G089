import sqlite3
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

#database
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#home
@app.route("/")
def home():
    if "user" in session:
        return render_template("dashboard.html")
    return render_template("index.html")

#register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed)
            )
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect("/login")

    return render_template("register.html")

#login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")

#logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

#create table 
if __name__ == "__main__":
    import sqlite3

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

    app.run(debug=True)