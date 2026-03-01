import sqlite3
import os

db_path = 'travel_cheatsheet.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("Starting manual migration v6...")
    
    new_columns = [
        ("practical_info", "tipping_culture", "TEXT"),
        ("practical_info", "drinking_age", "VARCHAR(100)"),
        ("practical_info", "alcohol_rules", "TEXT"),
        ("practical_info", "dress_code", "TEXT"),
        ("practical_info", "photography_restrictions", "TEXT"),
        ("practical_info", "sensitive_topics", "TEXT"),
        ("practical_info", "local_norms", "TEXT"),
        ("practical_info", "last_updated", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]

    for table, col, col_type in new_columns:
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            print(f"Added {col} to {table}")
        except sqlite3.OperationalError:
            print(f"{col} already exists in {table} or error occurred")

    conn.commit()
    conn.close()
    print("Migration v6 finished!")

if __name__ == "__main__":
    migrate()
