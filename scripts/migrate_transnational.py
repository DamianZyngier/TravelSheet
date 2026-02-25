import sqlite3
import os

def migrate():
    db_path = "travel_cheatsheet.db"
    if not os.path.exists(db_path):
        print("Database not found, no migration needed.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(unesco_places)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "is_transnational" not in columns:
            print("Adding 'is_transnational' column to 'unesco_places' table...")
            cursor.execute("ALTER TABLE unesco_places ADD COLUMN is_transnational BOOLEAN DEFAULT 0")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column 'is_transnational' already exists.")
            
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
