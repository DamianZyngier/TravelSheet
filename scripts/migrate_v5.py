import sqlite3
import os

db_path = 'travel_cheatsheet.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("Starting manual migration v5...")
    
    try:
        cur.execute("ALTER TABLE attractions ADD COLUMN booking_info TEXT")
        print("Added booking_info to attractions table")
    except sqlite3.OperationalError:
        print("booking_info already exists or error occurred")

    conn.commit()
    conn.close()
    print("Migration v5 finished!")

if __name__ == "__main__":
    migrate()
