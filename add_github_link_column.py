import sqlite3
import os

# Database path (adjust if running from different location)
DB_PATH = os.path.join('instance', 'asan_devnest.db')

def update_db():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return None

    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Add github_link column
        try:
            print("Adding github_link column...")
            cursor.execute("ALTER TABLE student_projects ADD COLUMN github_link TEXT")
            print("Success.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("Column github_link already exists.")
            else:
                print(f"Error adding github_link: {e}")

        conn.commit()
        print("Database updated successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_db()
