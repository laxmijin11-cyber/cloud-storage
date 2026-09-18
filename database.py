import sqlite3
from datetime import datetime

DB_NAME = "cloud_storage.db"

def init_db():
    """Create tables if they don't exist"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Files table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            filename TEXT NOT NULL,
            s3_key TEXT NOT NULL,
            version TEXT NOT NULL,
            backup_key TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)
    
    conn.commit()
    conn.close()

def create_user(username, hashed_password):
    """Register a new user"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def get_user(username):
    """Fetch user by username"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_file_record(username, filename, s3_key, version, backup_key):
    """Save file metadata"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO files (username, filename, s3_key, version, backup_key)
        VALUES (?, ?, ?, ?, ?)
    """, (username, filename, s3_key, version, backup_key))
    conn.commit()
    conn.close()

def get_file_versions(username, filename):
    """Get all versions of a file"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s3_key, version, uploaded_at, backup_key
        FROM files
        WHERE username = ? AND filename = ?
        ORDER BY uploaded_at DESC
    """, (username, filename))
    versions = cursor.fetchall()
    conn.close()
    return versions

def get_all_files(username):
    """Get all files for a user"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT filename, MAX(uploaded_at) as last_upload
        FROM files
        WHERE username = ?
        GROUP BY filename
        ORDER BY last_upload DESC
    """, (username,))
    files = cursor.fetchall()
    conn.close()
    return files