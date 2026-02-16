import sqlite3
import os

class GameDatabase:
    def __init__(self, db_path="game_data.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Table for game results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT UNIQUE,
                history TEXT,
                prediction TEXT,
                actual_outcome TEXT,
                confidence REAL,
                bet_amount REAL,
                is_win INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def save_result(self, period, history, prediction, actual_outcome, confidence, bet_amount):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        is_win = 1 if prediction == actual_outcome else 0
        try:
            cursor.execute('''
                INSERT INTO game_results (period, history, prediction, actual_outcome, confidence, bet_amount, is_win)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (period, ",".join(history), prediction, actual_outcome, confidence, bet_amount, is_win))
            conn.commit()
        except sqlite3.IntegrityError:
            # Period already exists, skip or update
            pass
        conn.close()

    def get_recent_results(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT actual_outcome FROM game_results ORDER BY id DESC LIMIT ?', (limit,))
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results
