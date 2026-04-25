from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

#DATABASE
def init_db():
    conn = sqlite3.connect("users.db")
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

def get_db():
    return sqlite3.connect("users.db")

# HOME 
@app.route("/")
def home():
    if "user" in session:
        return f"""
        <h2>Welcome, {session['user']}!</h2>
        <a href='/logout'>Logout</a>
        """
    
    return """
    <h2>Home</h2>
    <a href='/register'>Register</a> | <a href='/login'>Login</a>
    """

# REGISTER 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # STEP 2 → HASH PASSWORD
        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect("/login")

    return """
    <h2>Register</h2>
    <form method='POST'>
        Username: <input name='username'><br>
        Password: <input type='password' name='password'><br>
        <button type='submit'>Register</button>
    </form>
    """

# LOGIN 
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

        if user and check_password_hash(user[2], password):
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid login"

    return """
    <h2>Login</h2>
    <form method='POST'>
        Username: <input name='username'><br>
        Password: <input type='password' name='password'><br>
        <button type='submit'>Login</button>
    </form>
    """

# LOGOUT 
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

#  RUN
if __name__ == "__main__":
    init_db()
    app.run(debug=True)