import os
import subprocess
import sys
import shutil

def run_command(command, description):
    print(f"--- Running: {description} ---")
    try:
        # Use sys.executable to ensure we use the same python environment
        result = subprocess.run([sys.executable] + command.split(), check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    # 1. Clean up
    db_path = 'travel_cheatsheet.db'
    if os.path.exists(db_path):
        print(f"Cleaning up existing database: {db_path}")
        os.remove(db_path)
    
    docs_json = 'docs/data.json'
    if os.path.exists(docs_json):
        print(f"Cleaning up existing data.json: {docs_json}")
        # We don't necessarily need to remove it, but it's cleaner
        # os.remove(docs_json)

    # 2. Run Seed DB
    if not run_command("scripts/seed_db.py", "Database Seeding"):
        sys.exit(1)

    # 3. Run Export to JSON
    if not run_command("scripts/export_to_json.py", "Export to JSON"):
        sys.exit(1)

    # 4. Run Data Integrity Test
    if not run_command("scripts/test_data_integrity.py", "Data Integrity Test"):
        sys.exit(1)

    print("\n✨ All sync tasks (non-syncing part) passed successfully!")
    sys.exit(0)

if __name__ == "__main__":
    main()
