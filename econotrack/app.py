from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "econotrack_secret"


# DATABASE CONNECTION

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE + NEWS FEED

@app.route('/')
def index():

    conn = get_db()

    search = request.args.get('search', '')
    category = request.args.get('category', '')

    query = "SELECT * FROM news WHERE 1=1"
    params = []

    # SEARCH FEATURE
    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    # FILTER FEATURE
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


# REGISTER


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                'INSERT INTO users (email, password) VALUES (?, ?)',
                (email, hashed_password)
            )

            conn.commit()

        except:
            conn.close()
            return 'User already exists'

        conn.close()

        return redirect('/login')

    return render_template('register.html')


# LOGIN


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM users WHERE email=?',
            (email,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = email
            return redirect('/')

        else:
            return 'Invalid login'

    return render_template('login.html')


# LOGOUT


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# DASHBOARD


@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    try:
        news = conn.execute('SELECT * FROM news').fetchall()

    except:
        news = []

    conn.close()

    return render_template('dashboard.html', news=news)


# PROFILE MANAGEMENT


@app.route('/profile', methods=['GET', 'POST'])
def profile():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM users WHERE email=?',
        (session['user'],)
    )

    user = cursor.fetchone()

    if request.method == 'POST':

        new_email = request.form['email']

        cursor.execute(
            'UPDATE users SET email=? WHERE email=?',
            (new_email, session['user'])
        )

        conn.commit()

        session['user'] = new_email

        conn.close()

        return redirect('/profile')

    conn.close()

    return render_template('profile.html', user=user)


# ADD NEWS


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


# EDIT NEWS

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

    news = conn.execute(
        'SELECT * FROM news WHERE id=?',
        (id,)
    ).fetchone()

    conn.close()

    return render_template('edit.html', news=news)


# DELETE NEWS


@app.route('/delete/<int:id>')
def delete(id):

    conn = get_db()

    conn.execute(
        'DELETE FROM news WHERE id=?',
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# VIEW ARTICLE


@app.route('/view/<int:id>')
def view(id):

    conn = get_db()

    news = conn.execute(
        'SELECT * FROM news WHERE id=?',
        (id,)
    ).fetchone()

    conn.close()

    return render_template('view.html', news=news)


# CREATE DATABASE TABLES


def init_db():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    ''')

    # NEWS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()


# RUN APP


if __name__ == '__main__':

    init_db()

    app.run(debug=True)