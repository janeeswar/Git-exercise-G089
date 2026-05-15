from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3


app = Flask(__name__)
app.secret_key = "econotrack_secret"

def get_db_connection():
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():

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




if __name__ == "__main__":
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

    @app.route('/view/<int:id>')
def view(id):
    conn = get_db()
    news = conn.execute('SELECT * FROM news WHERE id=?', (id,)).fetchone()
    conn.close()

    return render_template('view.html', news=news)


# HOME
@app.route("/")
def home():
    if "user" in session:
        return render_template("dashboard.html")
    return render_template("index.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        hashed = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, hashed)
            )
            conn.commit()
        except:
            conn.close()
            return "User already exists"

        conn.close()
        return redirect("/login")

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = email
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# CREATE TABLE + RUN
if __name__ == "__main__":
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

    app.run(debug=True)
app.secret_key = "econotrack_secret"
def create_price_table():

    conn = sqlite3.connect("database.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource TEXT,
            price REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.close()

create_price_table()
@app.route("/add_prices")
def add_prices():

    conn = get_db_connection()

    # Sample Oil Prices
    conn.execute("INSERT INTO prices (resource, price) VALUES (?, ?)", ("Oil", 82.5))
    conn.execute("INSERT INTO prices (resource, price) VALUES (?, ?)", ("Oil", 84.2))

    # Sample Gold Prices
    conn.execute("INSERT INTO prices (resource, price) VALUES (?, ?)", ("Gold", 2310.4))
    conn.execute("INSERT INTO prices (resource, price) VALUES (?, ?)", ("Gold", 2298.7))

    conn.commit()
    conn.close()

    return "Prices Added Successfully"
@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    news = conn.execute("SELECT * FROM news").fetchall()

    oil_prices = conn.execute(
        "SELECT * FROM prices WHERE resource='Oil'"
    ).fetchall()

    gold_prices = conn.execute(
        "SELECT * FROM prices WHERE resource='Gold'"
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        news=news,
        oil_prices=oil_prices,
        gold_prices=gold_prices
    )
