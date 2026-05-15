import sqlite3
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

<<<<<<< HEAD
# Database connection
=======
# DATABASE
>>>>>>> cc85ea38287e663532f35054a3899f7f50e510d0
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
<<<<<<< HEAD


# 🟢 HOME ROUTE (Categorized Feed)
@app.route('/')
def index():
    conn = get_db()

    search = request.args.get('search', '')
    category = request.args.get('category', '')

    query = "SELECT * FROM news WHERE 1=1"
    params = []

    # Keyword Search
    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    # Category Filter
    if category:
        query += " AND category = ?"
        params.append(category)

    news = conn.execute(query, params).fetchall()
    conn.close()

    categorized = {}

    for item in news:
        cat = item['category']
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(item)

    return render_template(
        'index.html',
        categorized=categorized,
        search=search,
        category=category
    )


# 🟢 ADD NEWS
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']

        conn = get_db()
        conn.execute(
            'INSERT INTO news (title, content, category) VALUES (?, ?, ?)',
            (title, content, category)
        )
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add.html')


# 🟢 DELETE
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute('DELETE FROM news WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')


# 🟢 EDIT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']

        conn.execute(
            'UPDATE news SET title=?, content=?, category=? WHERE id=?',
            (title, content, category, id)
        )
        conn.commit()
        conn.close()

        return redirect('/')

    news = conn.execute('SELECT * FROM news WHERE id=?', (id,)).fetchone()
    conn.close()

    return render_template('edit.html', news=news)


# 🟢 VIEW ARTICLE
@app.route('/view/<int:id>')
def view(id):
    conn = get_db()
    news = conn.execute('SELECT * FROM news WHERE id=?', (id,)).fetchone()
    conn.close()

    return render_template('view.html', news=news)


# RUN APP
if __name__ == '__main__':
    app.run(debug=True)

    @app.route('/view/<int:id>')
def view(id):
    conn = get_db()
    news = conn.execute('SELECT * FROM news WHERE id=?', (id,)).fetchone()
    conn.close()

    return render_template('view.html', news=news)
=======

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
>>>>>>> cc85ea38287e663532f35054a3899f7f50e510d0
