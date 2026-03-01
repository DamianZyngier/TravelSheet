import sqlite3
import os

db_path = 'travel_cheatsheet.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE countries SET unique_animals = NULL WHERE unique_animals LIKE '%studies%'")
    print(f"Cleared {cur.rowcount} incorrect animal entries")
    conn.commit()
    conn.close()
