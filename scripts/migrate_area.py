import os
import sys
import sqlite3

# Path to DB
db_path = "travel_cheatsheet.db"

def migrate():
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding 'area' column to 'countries' table...")
        cursor.execute("ALTER TABLE countries ADD COLUMN area DECIMAL(15, 2)")
        conn.commit()
        print("Column added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("Column 'area' already exists.")
        else:
            print(f"Operational Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
