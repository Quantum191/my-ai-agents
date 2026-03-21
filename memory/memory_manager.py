import sqlite3
import os

# --- HARDCODED ABSOLUTE PATH ---
PROJECT_ROOT = "/home/sean/my-ai-agents"
MEMORY_DIR = os.path.join(PROJECT_ROOT, "memory")

class AgentMemory:
    def __init__(self):
        # SECURITY: Force the folder to exist BEFORE SQLite tries to open the file!
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.db_path = os.path.join(MEMORY_DIR, "agent_memory.db")
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT,
                    response TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database Init Error: {e}")

    def save_interaction(self, prompt, response):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO interactions (prompt, response) VALUES (?, ?)", 
                           (prompt, response))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database Save Error: {e}")

    # THE MISSING FUNCTION IS BACK!
    def get_recent_context(self, limit=5):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT prompt, response FROM interactions ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return "No recent history."
            
            context = []
            for row in reversed(rows):
                context.append(f"User: {row[0]}\nAgent: {row[1]}")
            return "\n\n".join(context)
        except Exception as e:
            return f"Database Read Error: {e}"
