import sqlite3
import os

db_path = 'travel_cheatsheet.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("Starting manual migration v4...")
    
    try:
        cur.execute("ALTER TABLE weather ADD COLUMN forecast_json TEXT")
        print("Added forecast_json to weather table")
    except sqlite3.OperationalError:
        print("forecast_json already exists or error occurred")

    conn.commit()
    conn.close()
    print("Migration v4 finished!")

if __name__ == "__main__":
    migrate()
