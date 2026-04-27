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
import sqlite3
import os

app = Flask(__name__)

# Helper to connect to SQLite
def get_db():
    db = sqlite3.connect('econotrack.db')
    db.row_factory = sqlite3.Row
    return db

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Creates an empty database file if it doesn't exist
    if not os.path.exists('econotrack.db'):
        conn = sqlite3.connect('econotrack.db')
        conn.close()
    
    app.run(debug=True)
 