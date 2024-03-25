import sqlite3

def db_connect():
    return sqlite3.connect(r'D:\GitHub\Skill-Resolution\course_platform.db')

# Fetch all modules
def fetch_modules():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM Modules''')
    modules = cursor.fetchall()
    conn.close()
    return modules

# Fetch lessons for a specific module
def fetch_lessons_for_module(module_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM Lessons WHERE ModuleID = ?''', (module_id,))
    lessons = cursor.fetchall()
    conn.close()
    return lessons