import sqlite3
import os

db_path = 'travel_cheatsheet.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("Starting manual migration v3...")
    
    new_columns = [
        ("countries", "alcohol_status", "VARCHAR(255)"),
        ("countries", "lgbtq_status", "VARCHAR(255)"),
        ("countries", "id_requirement", "VARCHAR(255)"),
        ("countries", "main_airport", "VARCHAR(255)"),
        ("countries", "railway_info", "VARCHAR(255)"),
        ("countries", "natural_hazards", "TEXT"),
        ("countries", "popular_apps", "VARCHAR(255)")
    ]

    for table, col, col_type in new_columns:
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            print(f"Added {col} to {table}")
        except sqlite3.OperationalError:
            print(f"{col} already exists in {table} or error occurred")

    conn.commit()
    conn.close()
    print("Migration v3 finished!")

if __name__ == "__main__":
    migrate()
