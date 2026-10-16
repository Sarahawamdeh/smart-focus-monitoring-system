"""Fill the database with demo data (fake instructor, courses and students)."""
import sqlite3
from werkzeug.security import generate_password_hash

DEMO_EMAIL = 'demo@example.com'
DEMO_PASSWORD = 'demo123'  # demo only - never reuse this anywhere real


def seed_demo_data():
    conn = sqlite3.connect('smart_focus.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')

    try:
        cursor.execute(
            "INSERT OR REPLACE INTO instructors (ins_id, fullname, email, password) VALUES (?, ?, ?, ?)",
            (1, 'Demo Instructor', DEMO_EMAIL, generate_password_hash(DEMO_PASSWORD)))

        courses = [
            ('cs332', 'Network'),
            ('cis342', 'System'),
            ('cs111L', 'Lab Python'),
            ('cis468', 'Big Data'),
            ('cis260', 'Database'),
        ]
        cursor.executemany("INSERT OR IGNORE INTO courses (course_code, course_name) VALUES (?, ?)", courses)

        # (course_code, ins_id, section_num)
        sections = [('cs332', 1, 1), ('cis342', 1, 2), ('cs111L', 1, 1), ('cis468', 1, 1), ('cis260', 1, 1)]
        cursor.executemany("INSERT OR IGNORE INTO sections (course_code, ins_id, section_num) VALUES (?, ?, ?)", sections)

        students = [(i, f'Student {i}') for i in range(1, 6)]
        cursor.executemany("INSERT OR IGNORE INTO students (student_id, student_name) VALUES (?, ?)", students)

        conn.commit()
        print(f"Demo data added. Sign in with {DEMO_EMAIL} / {DEMO_PASSWORD}")
    except sqlite3.Error as e:
        print(f"Error while seeding data: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    seed_demo_data()
