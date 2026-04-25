<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for
=======
import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
    @app.route('/')
def index():
    conn = get_db()
    news = conn.execute('SELECT * FROM news').fetchall()
    conn.close()
    return render_template('index.html', news=news)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>EconoTrack is Running!</h1>'

if __name__ == '__main__':
    app.run(debug=True)
    from flask import Flask, render_template
>>>>>>> 2eece93c3ab1753da5ffbe3d36b017a46da1905b
import sqlite3
import os

app = Flask(__name__)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('econotrack.db')
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)")

        conn.commit()
        conn.close()

        # ✅ redirect AFTER saving
        return redirect(url_for('index'))

    # ✅ show form if GET
    return render_template('register.html')


if __name__ == '__main__':
    if not os.path.exists('econotrack.db'):
        conn = sqlite3.connect('econotrack.db')
        conn.close()

    app.run(debug=True)
<<<<<<< HEAD
    @app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('econotrack.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            return redirect(url_for('index'))  # or dashboard later
        else:
            return "Invalid username or password"

    return render_template('login.html')
=======
 
>>>>>>> 2eece93c3ab1753da5ffbe3d36b017a46da1905b
