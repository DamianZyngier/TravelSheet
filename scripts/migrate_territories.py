import sqlite3
import os

db_path = 'travel_cheatsheet.db'

def migrate():
    print(f"Migrating database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Check if parent_id exists
        cur.execute("PRAGMA table_info(countries)")
        columns = [col[1] for col in cur.fetchall()]
        
        if 'parent_id' not in columns:
            print("Adding parent_id column to countries...")
            cur.execute("ALTER TABLE countries ADD COLUMN parent_id INTEGER REFERENCES countries(id)")
        else:
            print("parent_id column already exists.")
            
        if 'is_independent' not in columns:
            print("Adding is_independent column to countries...")
            cur.execute("ALTER TABLE countries ADD COLUMN is_independent BOOLEAN DEFAULT 1")
        else:
            print("is_independent column already exists.")
            
        conn.commit()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
