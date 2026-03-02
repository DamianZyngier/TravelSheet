import sqlite3
import os

db_path = 'travel_cheatsheet.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute(f"PRAGMA table_info(countries)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'climate_description' not in columns:
            print(f"Adding climate_description to countries...")
            cursor.execute(f"ALTER TABLE countries ADD COLUMN climate_description TEXT")
            print(f"✅ Column added.")
        else:
            print(f"ℹ️ Table already has climate_description column.")
    except Exception as e:
        print(f"❌ Error migrating: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
