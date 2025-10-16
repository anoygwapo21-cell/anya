from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret123'

# --- DATABASE CONFIG ---
DB_NAME = 'travel.db'

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS spots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                name TEXT,
                location TEXT,
                description TEXT,
                image TEXT
            )
        ''')
        # ---- SAMPLE DATA ----
        data = [
            # Cultural and Historical Sites
            ("Cultural and Historical Sites", "Magellan’s Cross", "Cebu City", "A historic Christian cross planted by Portuguese and Spanish explorers.", "magellans_cross.jpg"),
            ("Cultural and Historical Sites", "Basilica del Santo Niño", "Cebu City", "The oldest Roman Catholic church in the Philippines.", "basilica.jpg"),

            # City and Food Destinations
            ("City and Food Destinations", "Larsian BBQ", "Fuente Osmeña", "Famous open-air barbecue market for authentic Cebuano street food.", "city.jpg"),
            ("City and Food Destinations", "SM Seaside", "SRP, Cebu City", "A massive modern shopping and dining complex with an ocean view.", "city.jpg"),

            # Falls
            ("Falls", "Kawasan Falls", "Badian, Cebu", "A multi-layered waterfall known for its turquoise waters.", "kawasan.jpg"),
            ("Falls", "Dao Falls", "Samboan, Cebu", "A hidden gem surrounded by lush tropical forests.", "falls.jpg"),

            # Beach
            ("Beach", "Moalboal White Beach", "Moalboal, Cebu", "Perfect for diving and sardine run experiences.", "moalboal.jpg"),
            ("Beach", "Bantayan Island", "Northern Cebu", "Known for its powdery white sand and crystal-clear waters.", "bantayan.jpg")
        ]
        cur.executemany('INSERT INTO spots (category, name, location, description, image) VALUES (?, ?, ?, ?, ?)', data)
        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- USERS ---
users = {"test": "1234"}

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user in users and users[user] == pw:
            session['user'] = user
            return redirect(url_for('home'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        users[user] = pw
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    categories = ["Cultural and Historical Sites", "City and Food Destinations", "Falls", "Beach"]
    return render_template('home.html', user=session['user'], categories=categories)

@app.route('/category/<name>')
def category(name):
    categories = {
        "Beach": [
            {"name": "Bantayan Island", "location": "Bantayan, Cebu", "image": "bantayan.jpg", "description": "White sands, blue skies, and relaxed island vibes."},
            {"name": "Malapascua Island", "location": "Daanbantayan, Cebu", "image": "malapascua.jpg", "description": "Dive with thresher sharks in crystal-clear waters."},
            {"name": "Moalboal", "location": "Moalboal, Cebu", "image": "moalboal.jpg", "description": "Snorkel among the sardine run and vibrant coral reefs."}
        ],
        "Falls": [
            {"name": "Kawasan Falls", "location": "Badian, Cebu", "image": "kawasan.jpg", "description": "Iconic turquoise waterfalls for swimming and canyoneering."},
            {"name": "Tumalog Falls", "location": "Oslob, Cebu", "image": "tumalog.jpg", "description": "A gentle waterfall surrounded by lush greenery."},
            {"name": "Mantayupan Falls", "location": "Barili, Cebu", "image": "mantayupan.jpg", "description": "One of the tallest waterfalls in Cebu."}
        ],
        "City and Food Destinations": [
            {"name": "Colon Street", "location": "Cebu City", "image": "colon.jpg", "description": "The oldest street in the Philippines filled with shops and heritage."},
            {"name": "Carcar City", "location": "Carcar, Cebu", "image": "lechon.jpg", "description": "Taste the world-famous Cebu Lechon."},
            {"name": "Temple of Leah", "location": "Busay, Cebu", "image": "templeleah.jpg", "description": "Roman-inspired temple with panoramic city views."}
        ],
        "Cultural and Historical Sites": [
            {"name": "Magellan’s Cross", "location": "Cebu City", "image": "magellanscross.jpg", "description": "A symbol of Christianity’s arrival in the Philippines."},
            {"name": "Fort San Pedro", "location": "Cebu City", "image": "fortsanpedro.jpg", "description": "Oldest fort in the Philippines built during Spanish rule."},
            {"name": "Basilica del Santo Niño", "location": "Cebu City", "image": "basilica.jpg", "description": "Houses the image of Santo Niño de Cebu."}
        ]
    }

    spots = categories.get(name, [])
    return render_template("category.html", category=name, spots=spots)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
