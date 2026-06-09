from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = "econotrack_secret"


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE
@app.route('/')
def index():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    search = request.args.get('search', '')
    category = request.args.get('category', '')

    query = "SELECT * FROM news WHERE 1=1"
    params = []

    # SEARCH
    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    # FILTER
    if category:
        query += " AND category=?"
        params.append(category)

    news = conn.execute(query, params).fetchall()

    categorized = {}

    for item in news:

        cat = item['category']

        if cat not in categorized:
            categorized[cat] = []

        categorized[cat].append(item)

    conn.close()

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

        try:

            conn.execute(
                'INSERT INTO users (email, password) VALUES (?, ?)',
                (email, hashed_password)
            )

            conn.commit()

        except:
            conn.close()
            return "User already exists"

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

        user = conn.execute(
            'SELECT * FROM users WHERE email=?',
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user['password'], password):

            session['user'] = email

            return redirect('/')

        else:
            return "Invalid Login"

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

    return render_template('dashboard.html')

# PROFILE
@app.route('/profile', methods=['GET', 'POST'])
def profile():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    user = conn.execute(
        'SELECT * FROM users WHERE email=?',
        (session['user'],)
    ).fetchone()

    if request.method == 'POST':

        new_email = request.form['email']

        conn.execute(
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

        if not title or not content or not category:
            return "Please fill all fields"

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

    comments = conn.execute(
        'SELECT * FROM comments WHERE news_id=?',
        (id,)
    ).fetchall()

    likes = conn.execute(
        'SELECT COUNT(*) AS total FROM reactions WHERE news_id=?',
        (id,)
    ).fetchone()

    bookmarked = conn.execute(
        'SELECT * FROM bookmarks WHERE news_id=?',
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        'view.html',
        news=news,
        comments=comments,
        likes=likes['total'],
        bookmarked=bookmarked
    )


# COMMENT SYSTEM
@app.route('/comment/<int:id>', methods=['POST'])
def comment(id):

    username = request.form['username']
    comment = request.form['comment']

    if not username or not comment:
        return redirect(f'/view/{id}')

    conn = get_db()

    conn.execute(
        'INSERT INTO comments (news_id, username, comment) VALUES (?, ?, ?)',
        (id, username, comment)
    )

    conn.commit()

    conn.close()

    return redirect(f'/view/{id}')


# DELETE COMMENT
@app.route('/delete_comment/<int:id>/<int:news_id>')
def delete_comment(id, news_id):

    conn = get_db()

    conn.execute(
        'DELETE FROM comments WHERE id=?',
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect(f'/view/{news_id}')


# LIKE SYSTEM
@app.route('/like/<int:id>')
def like(id):

    conn = get_db()

    conn.execute(
        'INSERT INTO reactions (news_id, reaction) VALUES (?, ?)',
        (id, 'like')
    )

    conn.commit()

    conn.close()

    return redirect(f'/view/{id}')


# BOOKMARK SYSTEM
@app.route('/bookmark/<int:id>')
def bookmark(id):

    conn = get_db()

    existing = conn.execute(
        'SELECT * FROM bookmarks WHERE news_id=?',
        (id,)
    ).fetchone()

    if not existing:

        conn.execute(
            'INSERT INTO bookmarks (news_id) VALUES (?)',
            (id,)
        )

        conn.commit()

    conn.close()

    return redirect(f'/view/{id}')


# VIEW SAVED ARTICLES
@app.route('/bookmarks')
def bookmarks():

    conn = get_db()

    saved = conn.execute('''
        SELECT news.*
        FROM news
        JOIN bookmarks
        ON news.id = bookmarks.news_id
    ''').fetchall()

    conn.close()

    return render_template(
        'bookmarks.html',
        saved=saved
    )


# ADD SAMPLE PRICES
@app.route('/add_prices')
def add_prices():

    conn = get_db()

    conn.execute(
        "INSERT INTO prices (resource, price) VALUES (?, ?)",
        ("Oil", 82.5)
    )

    conn.execute(
        "INSERT INTO prices (resource, price) VALUES (?, ?)",
        ("Gold", 2310.4)
    )

    conn.commit()

    conn.close()

    return "Prices Added Successfully"


# CREATE DATABASE
def init_db():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    # USERS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    ''')

    # NEWS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        category TEXT
    )
    ''')

    # PRICES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource TEXT,
        price REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # COMMENTS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        news_id INTEGER,
        username TEXT,
        comment TEXT
    )
    ''')

    # REACTIONS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        news_id INTEGER,
        reaction TEXT
    )
    ''')

    # BOOKMARKS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        news_id INTEGER
    )
    ''')

    conn.commit()

    conn.close()

@app.route('/api/live-prices')
def live_prices():

    api_key = "CDAOC9EIUEHHQ8TK"

    oil_url = f"https://www.alphavantage.co/query?function=WTI&interval=daily&apikey={api_key}"
    gold_url = f"https://www.alphavantage.co/query?function=ALUMINUM&interval=daily&apikey={api_key}"

    try:
        oil_response = requests.get(oil_url, timeout=10).json()
        gold_response = requests.get(gold_url, timeout=10).json()

        oil_data = oil_response.get("data", [])[:5]
        gold_data = gold_response.get("data", [])[:5]

        if not oil_data or not gold_data:
            raise Exception("API data not available")

        labels = []
        oil_prices = []
        gold_prices = []

        for item in reversed(oil_data):
            labels.append(item["date"])
            oil_prices.append(float(item["value"]))

        for item in reversed(gold_data):
            gold_prices.append(float(item["value"]))

        latest_oil = oil_prices[-1]
        previous_oil = oil_prices[-2]

        latest_gold = gold_prices[-1]
        previous_gold = gold_prices[-2]

        oil_change = round(latest_oil - previous_oil, 2)
        gold_change = round(latest_gold - previous_gold, 2)

        if oil_change > 0:
            oil_prediction = "Oil prices are increasing. Petrol, transport, delivery, and production costs may rise."
            oil_impact = "Higher crude oil prices can increase daily living costs because many industries depend on fuel."
            oil_trend = "Increasing"
        elif oil_change < 0:
            oil_prediction = "Oil prices are decreasing. Fuel-related cost pressure may reduce."
            oil_impact = "Lower crude oil prices can reduce transport and logistics costs."
            oil_trend = "Decreasing"
        else:
            oil_prediction = "Oil prices are stable. No major fuel cost movement is expected."
            oil_impact = "Stable oil prices help businesses and consumers plan expenses better."
            oil_trend = "Stable"

        if gold_change > 0:
            gold_prediction = "Gold prices are increasing. Investors may be moving toward safer assets."
            gold_impact = "Higher gold prices may show rising inflation concerns, uncertainty, or market fear."
            gold_trend = "Increasing"
        elif gold_change < 0:
            gold_prediction = "Gold prices are decreasing. Investors may be moving back to riskier assets."
            gold_impact = "Lower gold prices may suggest reduced uncertainty or stronger market confidence."
            gold_trend = "Decreasing"
        else:
            gold_prediction = "Gold prices are stable. Market uncertainty may be low."
            gold_impact = "Stable gold prices suggest balanced investor confidence."
            gold_trend = "Stable"

        return {
            "labels": labels,
            "oil": oil_prices,
            "gold": gold_prices,
            "latest_oil": latest_oil,
            "latest_gold": latest_gold,
            "oil_change": oil_change,
            "gold_change": gold_change,
            "oil_trend": oil_trend,
            "gold_trend": gold_trend,
            "oil_prediction": oil_prediction,
            "gold_prediction": gold_prediction,
            "oil_impact": oil_impact,
            "gold_impact": gold_impact,
            "source": "Alpha Vantage live data"
        }

    except Exception as e:
        return {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "oil": [82.5, 84.2, 83.9, 85.4, 86.1],
            "gold": [2310, 2325, 2330, 2342, 2351],
            "latest_oil": 86.1,
            "latest_gold": 2351,
            "oil_change": 0.7,
            "gold_change": 9,
            "oil_trend": "Increasing",
            "gold_trend": "Increasing",
            "oil_prediction": "Oil prices are increasing. Petrol, transport, delivery, and production costs may rise.",
            "gold_prediction": "Gold prices are increasing. Investors may be moving toward safer assets.",
            "oil_impact": "Higher crude oil prices can increase daily living costs because many industries depend on fuel.",
            "gold_impact": "Higher gold prices may show rising inflation concerns, uncertainty, or market fear.",
            "source": "Backup demo data",
            "note": str(e)
        }
@app.route('/gold')
def gold_page():

    if 'user' not in session:
        return redirect('/login')

    db = get_db()

    gold_news = db.execute(
        "SELECT * FROM news WHERE LOWER(category) LIKE '%gold%' ORDER BY id DESC"
    ).fetchall()

    return render_template('gold.html', news=gold_news)


@app.route('/oil')
def oil_page():

    if 'user' not in session:
        return redirect('/login')

    db = get_db()

    oil_news = db.execute(
        "SELECT * FROM news WHERE LOWER(category) LIKE '%oil%' ORDER BY id DESC"
    ).fetchall()

    return render_template('oil.html', news=oil_news)  

@app.route('/compare')
def compare_page():

    if 'user' not in session:
        return redirect('/login')

    return render_template('compare.html')

#event impact helper function

def analyze_event_text(event_text, severity="Medium"):

    text = event_text.lower()

    event_model = {
        "War": {
            "keywords": ["war", "conflict", "attack", "missile", "military", "invasion", "tension", "weapon", "strike"],
            "weight": 35
        },
        "Inflation": {
            "keywords": ["inflation", "price increase", "cost of living", "interest rate", "expensive", "consumer prices", "rising prices"],
            "weight": 30
        },
        "Climate Issue": {
            "keywords": ["climate", "flood", "drought", "heatwave", "storm", "crop damage", "natural disaster", "rainfall"],
            "weight": 28
        },
        "Political Instability": {
            "keywords": ["election", "sanction", "government", "policy", "protest", "instability", "political", "minister"],
            "weight": 32
        }
    }

    commodity_model = {
        "Oil": {
            "keywords": ["oil", "crude", "petrol", "fuel", "energy", "supply", "opec", "barrel"],
            "weight": 18
        },
        "Gold": {
            "keywords": ["gold", "safe haven", "investor", "uncertainty", "market fear", "precious metal"],
            "weight": 18
        },
        "General Economy": {
            "keywords": ["economy", "business", "trade", "market", "consumer", "currency", "growth", "recession"],
            "weight": 15
        }
    }

    severity_model = {
        "Low": 10,
        "Medium": 25,
        "High": 40
    }

    event_scores = {}
    commodity_scores = {}
    detected_keywords = []

    for event_name, event_data in event_model.items():
        score = 0

        for keyword in event_data["keywords"]:
            if keyword in text:
                score += event_data["weight"]
                detected_keywords.append(keyword)

        event_scores[event_name] = score

    for commodity_name, commodity_data in commodity_model.items():
        score = 0

        for keyword in commodity_data["keywords"]:
            if keyword in text:
                score += commodity_data["weight"]
                detected_keywords.append(keyword)

        commodity_scores[commodity_name] = score

    main_event = max(event_scores, key=event_scores.get)
    main_commodity = max(commodity_scores, key=commodity_scores.get)

    event_score = event_scores[main_event]
    commodity_score = commodity_scores[main_commodity]
    severity_score = severity_model[severity]

    if event_score == 0:
        main_event = "General Economic Event"
        event_score = 15

    if commodity_score == 0:
        main_commodity = "General Economy"
        commodity_score = 10

    impact_score = event_score + commodity_score + severity_score

    if impact_score > 100:
        impact_score = 100

    risk_levels = [
        {"min": 80, "level": "Very High"},
        {"min": 60, "level": "High"},
        {"min": 40, "level": "Medium"},
        {"min": 0, "level": "Low"}
    ]

    risk_level = next(
        item["level"] for item in risk_levels if impact_score >= item["min"]
    )

    impact_templates = {
        "Oil": {
            "prediction": "This event may affect crude oil and fuel-related costs because the system detected: {keywords}.",
            "daily_life": "Petrol, transport, delivery fees, and daily goods may become more expensive.",
            "business": "Businesses may face higher logistics, delivery, production, and operating costs.",
            "student": "Students may spend more on transport, ride-hailing, and food delivery."
        },
        "Gold": {
            "prediction": "This event may increase demand for gold as a safer asset because the system detected: {keywords}.",
            "daily_life": "Gold jewellery and investment prices may rise due to market uncertainty.",
            "business": "Investors may become more cautious and may shift money into safer assets.",
            "student": "Students may not be directly affected, but family savings and investments may be influenced."
        },
        "General Economy": {
            "prediction": "This event may affect the wider economy because the system detected: {keywords}.",
            "daily_life": "Households may face higher living costs and lower purchasing power.",
            "business": "Businesses may face weaker demand, higher costs, or uncertain market conditions.",
            "student": "Students may face higher food, transport, and daily expenses."
        }
    }

    detected_keywords = list(set(detected_keywords))

    if len(detected_keywords) == 0:
        detected_keyword_text = "general economic uncertainty"
    else:
        detected_keyword_text = ", ".join(detected_keywords)

    selected_template = impact_templates[main_commodity]

    prediction = selected_template["prediction"].format(
        keywords=detected_keyword_text
    )

    reason = (
        "The system matched keywords from the article, calculated the event score, "
        "commodity score, and severity score, then selected the highest scoring result."
    )

    return {
        "event_text": event_text,
        "severity": severity,
        "main_event": main_event,
        "main_commodity": main_commodity,
        "impact_score": impact_score,
        "risk_level": risk_level,
        "detected_keywords": detected_keywords,
        "event_score": event_score,
        "commodity_score": commodity_score,
        "severity_score": severity_score,
        "reason": reason,
        "prediction": prediction,
        "daily_life": selected_template["daily_life"],
        "business": selected_template["business"],
        "student": selected_template["student"]
    }
#event impact analyzer 
@app.route("/impact", methods=["GET", "POST"])
def impact_analyzer():

    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":

        event_text = request.form["event_text"]
        severity = request.form["severity"]

        result = analyze_event_text(event_text, severity)

    return render_template("impact.html", result=result)

#article impact analyzer route 
@app.route("/analyze_article/<int:id>")
def analyze_article(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    news = conn.execute(
        "SELECT * FROM news WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    if not news:
        return "Article not found"

    article_text = news["title"] + " " + news["content"]

    result = analyze_event_text(article_text, "Medium")

    return render_template("impact.html", result=result)

# RUN APP
if __name__ == '__main__':

    init_db()

    app.run(debug=True)