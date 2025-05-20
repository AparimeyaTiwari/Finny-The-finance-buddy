import sqlite3

def init_db():
    conn = sqlite3.connect("finny.db")
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        fincoins INTEGER DEFAULT 100
    )
    """)
    
    # Goals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        target REAL,
        saved REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.commit()
    conn.close()

# Call this at bot startup
init_db()