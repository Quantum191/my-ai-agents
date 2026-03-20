import sqlite3
from datetime import datetime

class AgentMemory:
    def __init__(self, db_path="memory/agent_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                prompt TEXT,
                response TEXT
            )
        ''')
        conn.commit()
        conn.close() # EXPLICITLY CLOSING

    def save_interaction(self, prompt, response):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO interactions (timestamp, prompt, response) VALUES (?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prompt, response)
        )
        conn.commit()
        conn.close() # EXPLICITLY CLOSING

    def get_recent_context(self, limit=3):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT prompt, response FROM interactions ORDER BY id DESC LIMIT ?", 
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close() # EXPLICITLY CLOSING
            
            context = ""
            for p, r in reversed(rows):
                context += f"User: {p}\nAI: {r}\n"
            return context
        except Exception:
            return ""

    def get_count(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM interactions")
            count = cursor.fetchone()[0]
            conn.close() # EXPLICITLY CLOSING
            return count
        except Exception:
            return 0
