from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret123'

DB_NAME = 'travel.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # Create spots table
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
    # Create users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Sample spots
    cur.execute('SELECT COUNT(*) FROM spots')
    if cur.fetchone()[0] == 0:
        data = [
            ("Cultural and Historical Sites", "Magellan’s Cross", "Cebu City", "A historic Christian cross planted by Portuguese and Spanish explorers.", "magellanscross.jpg"),
            ("Cultural and Historical Sites", "Basilica del Santo Niño", "Cebu City", "The oldest Roman Catholic church in the Philippines.", "basilica.jpg"),
            ("City and Food Destinations", "Larsian BBQ", "Fuente Osmeña", "Famous open-air barbecue market for authentic Cebuano street food.", "city.jpg"),
            ("City and Food Destinations", "SM Seaside", "SRP, Cebu City", "A massive modern shopping and dining complex with an ocean view.", "city.jpg"),
            ("Falls", "Kawasan Falls", "Badian, Cebu", "A multi-layered waterfall known for its turquoise waters.", "kawasan.jpg"),
            ("Falls", "Dao Falls", "Samboan, Cebu", "A hidden gem surrounded by lush tropical forests.", "falls.jpg"),
            ("Beach", "Moalboal White Beach", "Moalboal, Cebu", "Perfect for diving and sardine run experiences.", "moalboal.jpg"),
            ("Beach", "Bantayan Island", "Northern Cebu", "Known for its powdery white sand and crystal-clear waters.", "bantayan.jpg")
        ]
        cur.executemany('INSERT INTO spots (category, name, location, description, image) VALUES (?, ?, ?, ?, ?)', data)
    # Admin user
    cur.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cur.fetchone()[0] == 0:
        cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin123'))
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username=? AND password=?', (user, pw))
        user_data = cur.fetchone()
        conn.close()
        if user_data:
            session['user'] = user
            session['logged_in'] = True
            flash(f"Welcome, {user}! You have successfully logged in.", "success")
            if user == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))
        flash("Invalid username or password.", "danger")
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (user, pw))
            conn.commit()
            flash("Registration successful! You can now log in.", "success")
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Try another one.", "warning")
            conn.close()
    return render_template('register.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    categories = ["Cultural and Historical Sites", "City and Food Destinations", "Falls", "Beach"]
    return render_template('home.html', user=session['user'], categories=categories)

@app.route('/admin')
def admin_dashboard():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    spots = conn.execute('SELECT * FROM spots').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', spots=spots)

@app.route('/add_spot', methods=['GET', 'POST'])
def add_spot():
    if 'user' not in session or session['user'] != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('login'))
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        image = request.form['image']
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO spots (category, name, location, description, image) VALUES (?, ?, ?, ?, ?)',
            (category, name, location, description, image)
        )
        conn.commit()
        conn.close()
        flash("New tourist spot added successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('add_spot.html')

@app.route('/edit_spot/<int:id>', methods=['GET', 'POST'])
def edit_spot(id):
    if 'user' not in session or session['user'] != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('login'))
    conn = get_db_connection()
    spot = conn.execute('SELECT * FROM spots WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        image = request.form['image']
        conn.execute('UPDATE spots SET category=?, name=?, location=?, description=?, image=? WHERE id=?',
                     (category, name, location, description, image, id))
        conn.commit()
        conn.close()
        flash("Spot updated successfully!", "info")
        return redirect(url_for('admin_dashboard'))
    conn.close()
    return render_template('edit_spot.html', spot=spot)

@app.route('/delete_spot/<int:id>')
def delete_spot(id):
    if 'user' not in session or session['user'] != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM spots WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("Spot deleted successfully!", "warning")
    return redirect(url_for('admin_dashboard'))

@app.route('/category/<name>')
def category(name):
    conn = get_db_connection()
    spots = conn.execute('SELECT * FROM spots WHERE category = ?', (name,)).fetchall()
    conn.close()
    return render_template("category.html", category=name, spots=spots)

@app.route('/spot/<int:id>')
def spot_detail(id):
    conn = get_db_connection()
    spot = conn.execute('SELECT * FROM spots WHERE id=?', (id,)).fetchone()
    conn.close()
    if not spot:
        flash("Spot not found.", "danger")
        return redirect(url_for('home'))
    return render_template("spot.html", spot=spot)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)