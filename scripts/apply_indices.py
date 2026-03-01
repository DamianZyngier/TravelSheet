import sqlite3
import os

db_path = 'travel_cheatsheet.db'

def apply_indices():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    tables_to_index = [
        "languages", "currencies", "safety_info", "embassies", "entry_requirements",
        "attractions", "unesco_places", "religions", "holidays", "weather",
        "climate", "laws_and_customs", "cost_of_living"
    ]

    print("Applying performance indices...")
    for table in tables_to_index:
        try:
            index_name = f"ix_{table}_country_id"
            cur.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} (country_id)")
            print(f"✅ Indexed country_id in {table}")
        except Exception as e:
            print(f"❌ Error indexing {table}: {e}")

    conn.commit()
    conn.close()
    print("Optimization finished!")

if __name__ == "__main__":
    apply_indices()
