import sqlite3
import os

# Database path (adjust if running from different location)
DB_PATH = os.path.join('instance', 'asan_devnest.db')

def update_db():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        # Try root
        if os.path.exists('asan_devnest.db'):
            print("Found database in root directory instead.")
            return 'asan_devnest.db'
        return None

    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Add closed_by_id column
        try:
            print("Adding closed_by_id column...")
            cursor.execute("ALTER TABLE student_projects ADD COLUMN closed_by_id INTEGER REFERENCES users(id)")
            print("Success.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("Column closed_by_id already exists.")
            else:
                print(f"Error adding closed_by_id: {e}")

        # Add confirmed_by_id column
        try:
            print("Adding confirmed_by_id column...")
            cursor.execute("ALTER TABLE student_projects ADD COLUMN confirmed_by_id INTEGER REFERENCES users(id)")
            print("Success.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("Column confirmed_by_id already exists.")
            else:
                print(f"Error adding confirmed_by_id: {e}")

        conn.commit()
        print("Database updated successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_db()
