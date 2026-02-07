import sqlite3
import os

# Database path
DB_PATH = os.path.join('instance', 'asan_devnest.db')

def update_db():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create project_milestones table
        print("Creating project_milestones table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES student_projects(id),
                title VARCHAR(100) NOT NULL,
                status VARCHAR(20) DEFAULT 'Pending',
                completed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Success.")

        conn.commit()
        print("Database updated successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_db()
