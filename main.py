# main.py - CORE SYSTEM ENGINE
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger('MAIN')

class AffillifyDominationSystem:
    """
    Core engine for the AFFILIFY Domination System.
    Handles database operations, account management, and target tracking.
    """
    
    def __init__(self, db_path: str = "affilify_data/affilify.db"):
        self.db_path = db_path
        self._init_db()
        logger.info("🏛️ Affillify Domination System Engine initialized")

    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                cookie_file TEXT,
                comments_today INTEGER DEFAULT 0,
                daily_quota INTEGER DEFAULT 50,
                health_score INTEGER DEFAULT 100,
                last_active TIMESTAMP
            )
        ''')
        
        # Targets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_url TEXT UNIQUE,
                creator_username TEXT,
                description TEXT,
                views INTEGER,
                likes INTEGER,
                comments INTEGER,
                status TEXT DEFAULT 'PENDING',
                discovered_at TIMESTAMP
            )
        ''')
        
        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                video_url TEXT,
                comment_text TEXT,
                posted_at TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_available_account(self) -> Optional[Tuple]:
        """Get an account that hasn't reached its daily quota."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, cookie_file, comments_today, daily_quota 
            FROM accounts 
            WHERE comments_today < daily_quota 
            ORDER BY last_active ASC LIMIT 1
        ''')
        account = cursor.fetchone()
        conn.close()
        return account

    def get_next_target_video(self) -> Optional[Tuple]:
        """Get the next pending target video."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, video_url, creator_username, description 
            FROM targets 
            WHERE status = 'PENDING' 
            ORDER BY views DESC LIMIT 1
        ''')
        target = cursor.fetchone()
        conn.close()
        return target

    def record_comment(self, account_id: int, video_url: str, comment_text: str):
        """Record a successful comment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO comments (account_id, video_url, comment_text, posted_at)
            VALUES (?, ?, ?, ?)
        ''', (account_id, video_url, comment_text, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def update_account_activity(self, account_id: int, increment_comments: bool = True):
        """Update account activity timestamp and comment count."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if increment_comments:
            cursor.execute('''
                UPDATE accounts SET comments_today = comments_today + 1, last_active = ? WHERE id = ?
            ''', (datetime.now().isoformat(), account_id))
        else:
            cursor.execute('''
                UPDATE accounts SET last_active = ? WHERE id = ?
            ''', (datetime.now().isoformat(), account_id))
        conn.commit()
        conn.close()

    def mark_video_commented(self, video_id: int):
        """Mark a video as commented."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE targets SET status = "COMMENTED" WHERE id = ?', (video_id,))
        conn.commit()
        conn.close()

    def update_account_health(self, account_id: int, change: int):
        """Update account health score."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET health_score = health_score + ? WHERE id = ?', (change, account_id))
        conn.commit()
        conn.close()

    def add_target_video(self, video_url: str, creator_username: str, description: str, views: int, likes: int, comments: int):
        """Add a new target video to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO targets (video_url, creator_username, description, views, likes, comments, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (video_url, creator_username, description, views, likes, comments, datetime.now().isoformat()))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # Already exists
        conn.close()

    def get_dashboard_stats(self) -> Dict:
        """Get statistics for the dashboard."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM comments')
        total_comments = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM accounts')
        total_accounts = cursor.fetchone()[0]
        
        conn.close()
        return {
            'total_comments': total_comments,
            'total_accounts': total_accounts
        }
