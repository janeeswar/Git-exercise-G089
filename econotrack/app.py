import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Database connection
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# 🟢 HOME ROUTE (Categorized Feed)
@app.route('/')
def index():
    conn = get_db()
    news = conn.execute('SELECT * FROM news').fetchall()
    conn.close()

    categorized = {}

    for item in news:
        cat = item['category']
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(item)

    return render_template('index.html', categorized=categorized)


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