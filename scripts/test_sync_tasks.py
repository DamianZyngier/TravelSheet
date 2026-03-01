import os
import subprocess
import sys
import shutil

def run_command(command, description, env=None):
    print(f"--- Running: {description} ---")
    current_env = os.environ.copy()
    if env:
        current_env.update(env)
        
    try:
        # Use sys.executable to ensure we use the same python environment
        result = subprocess.run([sys.executable] + command.split(), check=True, capture_output=True, text=True, env=current_env)
        print(f"✅ {description} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    # 1. Setup temporary paths
    test_db = 'test_travel_cheatsheet.db'
    test_json = 'docs/test_data.json'
    
    # Clean up test files if they exist
    for f in [test_db, test_json]:
        if os.path.exists(f):
            os.remove(f)
            
    test_env = {
        'DATABASE_URL': f'sqlite:///./{test_db}',
        'DB_PATH': test_db,
        'JSON_OUTPUT_PATH': test_json
    }

    # 2. Run Seed DB (uses DATABASE_URL)
    if not run_command("scripts/seed_db.py", "Database Seeding", env=test_env):
        sys.exit(1)

    # 3. Run Export to JSON (uses DB_PATH and JSON_OUTPUT_PATH)
    if not run_command("scripts/export_to_json.py", "Export to JSON", env=test_env):
        sys.exit(1)

    # 4. Run Data Integrity Test (uses command line argument)
    if not run_command(f"scripts/test_data_integrity.py {test_json}", "Data Integrity Test"):
        sys.exit(1)

    # 5. Clean up
    if os.path.exists(test_db):
        os.remove(test_db)
    # We leave test_json for inspection if needed, or remove it
    if os.path.exists(test_json):
        os.remove(test_json)

    print("\n✨ All sync tasks (non-syncing part) passed successfully using temporary test files!")
    sys.exit(0)

if __name__ == "__main__":
    main()
