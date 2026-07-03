from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import requests
import feedparser
import os 

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "econotrack_secret")


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

    return render_template('index.html')

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

            if user['is_active'] == 0:
                return "Account is deactivated. Please contact admin."

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

    if 'user' not in session:
        return redirect('/login')

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

    if 'user' not in session:
        return redirect('/login')

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

    if 'user' not in session:
        return redirect('/login')

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

    if 'user' not in session:
        return redirect('/login')

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
        'SELECT * FROM bookmarks WHERE news_id=? AND user_email=?',
        (id, session['user'])
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

    if 'user' not in session:
        return redirect('/login')

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

    if 'user' not in session:
        return redirect('/login')

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

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    existing = conn.execute(
        'SELECT * FROM bookmarks WHERE news_id=? AND user_email=?',
        (id, session['user'])
    ).fetchone()

    if existing:
        conn.execute(
            'DELETE FROM bookmarks WHERE news_id=? AND user_email=?',
            (id, session['user'])
        )
    else:
        conn.execute(
            'INSERT INTO bookmarks (news_id, user_email) VALUES (?, ?)',
            (id, session['user'])
        )

    conn.commit()
    conn.close()

    return redirect(f'/view/{id}')

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
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
    except:
        pass

    # NEWS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        category TEXT
    )
    ''')

    try:
        cursor.execute("ALTER TABLE news ADD COLUMN source_name TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE news ADD COLUMN source_link TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE news ADD COLUMN why_matters TEXT")
    except:
        pass

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
        news_id INTEGER,
        user_email TEXT
    )
    ''')

    try:
        cursor.execute("ALTER TABLE bookmarks ADD COLUMN user_email TEXT")
    except:
        pass

        # PRICE ALERTS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        commodity TEXT,
        condition TEXT,
        target_price REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    try:
        cursor.execute("ALTER TABLE alerts ADD COLUMN user_email TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE alerts ADD COLUMN commodity TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE alerts ADD COLUMN condition TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE alerts ADD COLUMN target_price REAL")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE alerts ADD COLUMN created_at TIMESTAMP")
    except:
        pass

    conn.commit()
    conn.close()

    # BOOKMARK
@app.route('/bookmarks')
def bookmarks():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    saved = conn.execute('''
        SELECT news.*
        FROM news
        JOIN bookmarks
        ON news.id = bookmarks.news_id
        WHERE bookmarks.user_email=?
        ORDER BY bookmarks.id DESC
    ''', (session['user'],)).fetchall()

    conn.close()

    return render_template(
        'bookmarks.html',
        saved=saved
    )
   

@app.route('/api/live-prices')
def live_prices():

    oil_url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?range=5d&interval=1d"
    gold_url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=5d&interval=1d"

    def get_yahoo_prices(url):
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=10).json()

        result = response["chart"]["result"][0]
        timestamps = result["timestamp"]
        close_prices = result["indicators"]["quote"][0]["close"]

        labels = []
        prices = []

        from datetime import datetime

        for i in range(len(close_prices)):
            if close_prices[i] is not None:
                date = datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
                labels.append(date)
                prices.append(round(float(close_prices[i]), 2))

        return labels[-5:], prices[-5:]

    def calculate_impact(prices, commodity):

        if len(prices) < 2:
            return {
                "latest": 0,
                "change": 0,
                "percent_change": 0,
                "volatility": 0,
                "trend": "Unavailable",
                "impact_score": 0,
                "risk_level": "Unavailable",
                "prediction": f"{commodity} data is currently unavailable.",
                "impact": f"The system could not calculate {commodity.lower()} impact because price data was unavailable."
            }

        latest = prices[-1]
        previous = prices[-2]

        change = round(latest - previous, 2)
        percent_change = round((change / previous) * 100, 2)

        average = sum(prices) / len(prices)

        volatility = round(
            sum(abs(price - average) for price in prices) / len(prices),
            2
        )

        if change > 0:
            trend = "Increasing"
        elif change < 0:
            trend = "Decreasing"
        else:
            trend = "Stable"

        impact_score = abs(percent_change) * 20
        impact_score += volatility * 2

        if trend == "Increasing":
            impact_score += 25
        elif trend == "Decreasing":
            impact_score += 10
        else:
            impact_score += 5

        impact_score = round(impact_score)

        if impact_score > 100:
            impact_score = 100

        if impact_score >= 80:
            risk_level = "Very High"
        elif impact_score >= 60:
            risk_level = "High"
        elif impact_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        prediction = (
            f"{commodity} is {trend.lower()} by {change} "
            f"({percent_change}%). The impact score is "
            f"{impact_score}/100, showing a {risk_level.lower()} risk level."
        )

        if commodity == "Oil":
            impact = (
                "This is calculated from crude oil futures price movement, percentage change, "
                "volatility, and trend direction. A higher oil score may affect fuel, "
                "transport, delivery, and business costs."
            )
        else:
            impact = (
                "This is calculated from gold futures price movement, percentage change, "
                "volatility, and trend direction. A higher gold score may show stronger "
                "market uncertainty or safe-haven demand."
            )

        return {
            "latest": latest,
            "change": change,
            "percent_change": percent_change,
            "volatility": volatility,
            "trend": trend,
            "impact_score": impact_score,
            "risk_level": risk_level,
            "prediction": prediction,
            "impact": impact
        }

    oil_note = ""
    gold_note = ""

    try:
        oil_labels, oil_prices = get_yahoo_prices(oil_url)
    except Exception as e:
        oil_labels = []
        oil_prices = []
        oil_note = str(e)

    try:
        gold_labels, gold_prices = get_yahoo_prices(gold_url)
    except Exception as e:
        gold_labels = []
        gold_prices = []
        gold_note = str(e)

    labels = oil_labels if oil_labels else gold_labels

    oil_result = calculate_impact(oil_prices, "Oil")
    gold_result = calculate_impact(gold_prices, "Gold")

    if not labels:
        labels = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]

    if not oil_prices:
        oil_prices = [0, 0, 0, 0, 0]

    if not gold_prices:
        gold_prices = [0, 0, 0, 0, 0]

    return {
        "labels": labels,
        "oil": oil_prices,
        "gold": gold_prices,

        "latest_oil": oil_result["latest"],
        "latest_gold": gold_result["latest"],

        "oil_change": oil_result["change"],
        "gold_change": gold_result["change"],

        "oil_trend": oil_result["trend"],
        "gold_trend": gold_result["trend"],

        "oil_prediction": oil_result["prediction"],
        "gold_prediction": gold_result["prediction"],

        "oil_impact": oil_result["impact"],
        "gold_impact": gold_result["impact"],

        "oil_percent_change": oil_result["percent_change"],
        "gold_percent_change": gold_result["percent_change"],

        "oil_volatility": oil_result["volatility"],
        "gold_volatility": gold_result["volatility"],

        "oil_impact_score": oil_result["impact_score"],
        "gold_impact_score": gold_result["impact_score"],

        "oil_risk_level": oil_result["risk_level"],
        "gold_risk_level": gold_result["risk_level"],

        "source": "Yahoo Finance commodity futures data",
        "oil_note": oil_note,
        "gold_note": gold_note
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

# NEWS PAGE
@app.route('/news')
def news_page():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    search = request.args.get('search', '')
    category = request.args.get('category', '')

    query = "SELECT * FROM news WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    if category:
        query += " AND category=?"
        params.append(category)

    query += " ORDER BY id DESC"

    news = conn.execute(query, params).fetchall()

    categorized = {}

    for item in news:
        cat = item['category']

        if cat not in categorized:
            categorized[cat] = []

        categorized[cat].append(item)

    conn.close()

    return render_template(
        'news.html',
        categorized=categorized,
        search=search,
        category=category
    )

#fetch news 
@app.route('/fetch_news')
def fetch_news():

    if 'user' not in session:
        return redirect('/login')

    feeds = [
    {
        "source": "CNBC",
        "url": "https://www.cnbc.com/id/100727362/device/rss/rss.html"
    },
    {
        "source": "BBC Business",
        "url": "http://feeds.bbci.co.uk/news/business/rss.xml"
    },
    {
        "source": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rssindex"
    },
    {
        "source": "Investing.com",
        "url": "https://www.investing.com/rss/news.rss"
    }
]
    conn = get_db()

    for feed in feeds:

        parsed_feed = feedparser.parse(feed["url"])

        for entry in parsed_feed.entries[:20]:

            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")

            text = (title + " " + summary).lower()

            category = "Economy"

            if "oil" in text or "fuel" in text or "crude" in text:
                category = "Oil"
            elif "gold" in text or "safe haven" in text:
                category = "Gold"
            elif "war" in text or "conflict" in text or "attack" in text:
                category = "War"
            elif "inflation" in text or "interest rate" in text or "cost of living" in text:
                category = "Inflation"
            elif "climate" in text or "flood" in text or "drought" in text:
                category = "Climate"
            elif "politic" in text or "election" in text or "government" in text:
                category = "Politics"

            why_matters = "This article may affect market confidence, commodity prices, or daily living costs."

            if category == "Oil":
                why_matters = "This article may affect crude oil supply, fuel prices, transport costs, and business expenses."
            elif category == "Gold":
                why_matters = "This article may affect gold demand, investor confidence, and safe-haven investment behaviour."
            elif category == "War":
                why_matters = "This article may increase uncertainty and affect oil supply, gold demand, and global market stability."
            elif category == "Inflation":
                why_matters = "This article may affect consumer prices, purchasing power, interest rates, and cost of living."
            elif category == "Climate":
                why_matters = "This article may affect agriculture, supply chains, food prices, and commodity availability."
            elif category == "Politics":
                why_matters = "This article may affect investor confidence, policy decisions, currency movement, and market stability."

            existing = conn.execute(
                "SELECT * FROM news WHERE source_link=?",
                (link,)
            ).fetchone()

            if not existing and title and link:

                conn.execute(
                    '''
                    INSERT INTO news 
                    (title, content, category, source_name, source_link, why_matters)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (title, summary, category, feed["source"], link, why_matters)
                )

    conn.commit()
    conn.close()

    return redirect('/news')

# LIVE OIL PRICE CHANGE HELPER
def get_live_oil_change_percent():

    oil_url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?range=5d&interval=1d"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(oil_url, headers=headers, timeout=10).json()

        result = response["chart"]["result"][0]
        close_prices = result["indicators"]["quote"][0]["close"]

        prices = []

        for price in close_prices:
            if price is not None:
                prices.append(float(price))

        if len(prices) < 2:
            return 0

        latest = prices[-1]
        previous = prices[-2]

        percent_change = ((latest - previous) / previous) * 100

        return round(percent_change, 2)

    except:
        return 0

#student budget impact calculator
@app.route('/budget', methods=['GET', 'POST'])
def budget_calculator():

    if 'user' not in session:
        return redirect('/login')

    result = None

    if request.method == 'POST':

        fuel_spending = float(request.form['fuel_spending'])
        transport_spending = float(request.form['transport_spending'])
        food_delivery_spending = float(request.form['food_delivery_spending'])
        oil_change_percent = get_live_oil_change_percent()

        fuel_extra = round(fuel_spending * oil_change_percent / 100, 2)
        transport_extra = round(transport_spending * (oil_change_percent * 0.6) / 100, 2)
        delivery_extra = round(food_delivery_spending * (oil_change_percent * 0.4) / 100, 2)

        total_extra = round(fuel_extra + transport_extra + delivery_extra, 2)

        current_total = round(
            fuel_spending + transport_spending + food_delivery_spending,
            2
        )

        new_total = round(current_total + total_extra, 2)

        if total_extra >= 50:
            risk_level = "High"
            advice = "Try reducing fuel use, carpooling, or limiting delivery orders."
        elif total_extra >= 20:
            risk_level = "Medium"
            advice = "Your spending may increase slightly. Plan your weekly transport and food delivery carefully."
        else:
            risk_level = "Low"
            advice = "The increase is small, but it is still good to track your monthly spending."

        result = {
            "fuel_spending": fuel_spending,
            "transport_spending": transport_spending,
            "food_delivery_spending": food_delivery_spending,
            "oil_change_percent": oil_change_percent,
            "fuel_extra": fuel_extra,
            "transport_extra": transport_extra,
            "delivery_extra": delivery_extra,
            "total_extra": total_extra,
            "current_total": current_total,
            "new_total": new_total,
            "risk_level": risk_level,
            "advice": advice
        }

    return render_template('budget.html', result=result)

# PRICE ALERTS
@app.route('/alerts', methods=['GET', 'POST'])
def alerts():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    if request.method == 'POST':

        commodity = request.form['commodity']
        condition = request.form['condition']
        target_price = request.form['target_price']

        conn.execute(
            '''
            INSERT INTO alerts (user_email, commodity, condition, target_price)
            VALUES (?, ?, ?, ?)
            ''',
            (session['user'], commodity, condition, target_price)
        )

        conn.commit()

        conn.close()

        return redirect('/alerts')

    user_alerts = conn.execute(
        '''
        SELECT * FROM alerts
        WHERE user_email=?
        ORDER BY id DESC
        ''',
        (session['user'],)
    ).fetchall()

    conn.close()

    return render_template('alerts.html', alerts=user_alerts)


@app.route('/delete_alert/<int:id>')
def delete_alert(id):

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    conn.execute(
        'DELETE FROM alerts WHERE id=? AND user_email=?',
        (id, session['user'])
    )

    conn.commit()
    conn.close()

    return redirect('/alerts')

# ADMIN USER MANAGEMENT
ADMIN_EMAILS = [
    "janeeswar21@gmail.com",
    "test@gmail.com",
    "linghernther.12@gmail.com",
    "sham13ska@gmail.com"
]

@app.route('/admin/users')
def admin_users():

    if 'user' not in session:
        return redirect('/login')

    if session['user'] not in ADMIN_EMAILS:
        return "Access denied. Admin only."
 
    conn = get_db()

    users = conn.execute(
        'SELECT id, email, is_active FROM users ORDER BY id DESC'
    ).fetchall()

    conn.close()

    return render_template('admin_users.html', users=users)


@app.route('/admin/toggle_user/<int:id>')
def toggle_user(id):

    if 'user' not in session:
        return redirect('/login')

    if session['user'] not in ADMIN_EMAILS:
        return "Access denied. Admin only."
    conn = get_db()

    user = conn.execute(
        'SELECT * FROM users WHERE id=?',
        (id,)
    ).fetchone()

    if user:

        if user['is_active'] == 1:
            new_status = 0
        else:
            new_status = 1

        conn.execute(
            'UPDATE users SET is_active=? WHERE id=?',
            (new_status, id)
        )

        conn.commit()

    conn.close()

    return redirect('/admin/users')

# RUN APP
init_db()

if __name__ == '__main__':

    app.run(debug=False)