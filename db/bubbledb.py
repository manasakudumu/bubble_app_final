# db.py
import sqlite3

def get_connection():
    return sqlite3.connect("bubbledb.db", check_same_thread=False)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        name TEXT,
        role TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def add_user(email, name, role):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR IGNORE INTO users (email, name, role) VALUES (?, ?, ?)
    ''', (email, name, role))
    
    conn.commit()
    conn.close()

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    conn.close()
    return user


def create_journal_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        date TEXT,
        location TEXT,
        meal TEXT,
        food_name TEXT,
        mood TEXT,
        rating INTEGER,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def add_journal_entry(email, date, location, meal, food_name, mood, rating, comments):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO journal_entries (
        user_email, date, location, meal, food_name, mood, rating, comments
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (email, date, location, meal, food_name, mood, rating, comments))
    conn.commit()
    conn.close()

def get_journal_entries(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT date, location, meal, food_name, mood, rating, comments, created_at
    FROM journal_entries
    WHERE user_email = ?
    ORDER BY created_at DESC
    ''', (email,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE email = ?', (email,))
    conn.commit()
    conn.close()

