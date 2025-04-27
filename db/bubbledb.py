# db.py
import sqlite3

def get_connection():
    return sqlite3.connect("bubbledb.db", check_same_thread=False)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, name TEXT, role TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def add_user(email, name, role):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR REPLACE INTO users (email, name, role)
    VALUES (?, ?, ?)
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

def get_user_image(email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT image FROM users WHERE email = ?', (email,))
    image = cursor.fetchone()

    conn.close()
    
    if image:
        return image[0] 
    else:
        return None

def update_profile(preferred_name, class_year, pronouns, image):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE users
    SET preferred_name = ?, class_year = ?, pronouns = ?
    WHERE email = ?
    ''', (preferred_name, class_year, pronouns, image))

    conn.commit()
    conn.close()

def alter_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    # Add missing columns
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN preferred_name TEXT")
    except sqlite3.OperationalError:
        pass  # Ignore if the column already exists

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN class_year TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN pronouns TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN image BLOB")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


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

#for debugging and tetsing- can be ignored
def delete_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE email = ?', (email,))
    conn.commit()
    conn.close()


def drop_community_posts_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS community_posts")
    conn.commit()
    conn.close()

def create_posts_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_posts (
            id TEXT PRIMARY KEY,
            user_email TEXT,
            image_path TEXT,
            caption TEXT,
            rating INTEGER,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_community_post(post_id, user_email, image_path, caption, rating, created_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO community_posts (id, user_email, image_path, caption, rating, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (post_id, user_email, image_path, caption, rating, created_at))
    conn.commit()
    conn.close()

def get_all_community_posts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT id, user_email, image_path, caption, rating, created_at FROM community_posts ORDER BY created_at DESC""")
    return cursor.fetchall()

def create_feedback_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT,submitted_at TEXT)""")
    conn.commit()
    conn.close()

def submit_feedback(message, submitted_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO feedback (message, submitted_at)VALUES (?, ?)""", (message, submitted_at))
    conn.commit()
    conn.close()

def get_all_feedback():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" SELECT message, submitted_at FROM feedback ORDER BY submitted_at DESC""")
    return cursor.fetchall()

def delete_community_post(post_id):
    conn = sqlite3.connect("bubbledb.db")
    c = conn.cursor()
    c.execute("DELETE FROM community_posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def clear_all_community_posts():
    conn = sqlite3.connect("bubbledb.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM community_posts")
    conn.commit()
    conn.close()


