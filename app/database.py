import sqlite3
from datetime import datetime
from app.security import SecurityUtils

class DatabaseManager:
    def __init__(self, db_name='emergency_app.db'):
        """Initialize database connection and ensure tables exist."""
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        """Create and return a connection to the SQLite database."""
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """Create necessary tables with enhanced schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                emergency_contact_1 TEXT,
                emergency_contact_2 TEXT,
                registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                login_attempts INTEGER DEFAULT 0,
                is_locked BOOLEAN DEFAULT 0,
                lock_time DATETIME
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                author_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY(author_id) REFERENCES users(id)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                emergency_type TEXT,
                location TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'initiated',
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                device_id TEXT NOT NULL,
                device_hash TEXT NOT NULL,
                last_access DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, device_id)
            )
            ''')
            conn.commit()

    def register_user(self, phone, name, password, email=None):
        """Register a new user in the database."""
        try:
            hashed_password = SecurityUtils.hash_password(password)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (phone, name, password, email)
                    VALUES (?, ?, ?, ?)
                ''', (phone, name, hashed_password, email))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, phone, password):
        """Authenticate user with phone number and password."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE phone = ?', (phone,))
            result = cursor.fetchone()
        if result and SecurityUtils.verify_password(result[0], password):
            return True
        return False

    def get_user_by_phone(self, phone):
        """Get user by phone number."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, phone, name, email, emergency_contact_1, emergency_contact_2, registration_date
            FROM users WHERE phone = ?
            ''', (phone,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'phone': result[1],
                    'name': result[2],
                    'email': result[3],
                    'emergency_contact_1': result[4],
                    'emergency_contact_2': result[5],
                    'registration_date': result[6]
                }
            return None

    def register_device(self, user_id, device_id):
        """Register a device for automatic login."""
        device_hash = SecurityUtils.get_device_hash(device_id, user_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                INSERT OR REPLACE INTO device_auth 
                (user_id, device_id, device_hash, last_access, is_active)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
                ''', (user_id, device_id, device_hash))
                conn.commit()
                return True
            except sqlite3.Error:
                return False

    def get_user_by_device(self, device_id):
        """Get user data if device is registered."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT u.id, u.phone, u.name, u.email, u.emergency_contact_1, 
                   u.emergency_contact_2, u.registration_date
            FROM users u
            JOIN device_auth d ON u.id = d.user_id
            WHERE d.device_id = ? AND d.is_active = 1
            ''', (device_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'phone': result[1],
                    'name': result[2],
                    'email': result[3],
                    'emergency_contact_1': result[4],
                    'emergency_contact_2': result[5],
                    'registration_date': result[6]
                }
            return None
