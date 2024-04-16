from flask import Flask, render_template, request, redirect
import sqlite3
import string
import random

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 original_url TEXT NOT NULL,
                 short_url TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

# Function to generate a random string for shortened URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))  # Generate a 6-character short URL

# Function to shorten URL
def shorten_url(original_url):
    short_url = generate_short_url()
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO urls (original_url, short_url) VALUES (?, ?)", (original_url, short_url))
        conn.commit()
        conn.close()
        return short_url
    except sqlite3.IntegrityError:
        # If the generated short URL already exists, try again
        conn.close()
        return shorten_url(original_url)

# Retrieve original URL from database using shortened URL
def get_original_url(short_url):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_url=?", (short_url,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['original_url']
    short_url = shorten_url(original_url)
    return render_template('shorten.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_short_url(short_url):
    original_url = get_original_url(short_url)
    if original_url:
        return redirect(original_url)
    else:
        return "URL not found"

if __name__ == '__main__':
    init_db()  # Initialize database if not already initialized
    app.run(debug=True)
