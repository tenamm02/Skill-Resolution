import sqlite3

# Function to create tables in the database
def create_tables():
    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(r'D:\GitHub\Skill-Resolution\course_platform.db')
    
    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # SQL commands to create tables
    create_table_commands = [
        '''CREATE TABLE IF NOT EXISTS Users (UserID INTEGER PRIMARY KEY, UserName TEXT, UserEmail TEXT UNIQUE, RegistrationDate DATE);''',
        '''CREATE TABLE IF NOT EXISTS Modules (ModuleID INTEGER PRIMARY KEY, ModuleTitle TEXT, ModuleDescription TEXT);''',
        '''CREATE TABLE IF NOT EXISTS Lessons (LessonID INTEGER PRIMARY KEY, ModuleID INTEGER, LessonTitle TEXT, LessonContent TEXT, FOREIGN KEY (ModuleID) REFERENCES Modules (ModuleID));''',
        '''CREATE TABLE IF NOT EXISTS Articles (ArticleID INTEGER PRIMARY KEY, LessonID INTEGER, ArticleTitle TEXT, ArticleContent TEXT, FOREIGN KEY (LessonID) REFERENCES Lessons (LessonID));''',
        '''CREATE TABLE IF NOT EXISTS Quizzes (QuizID INTEGER PRIMARY KEY, LessonID INTEGER, QuizContent TEXT, FOREIGN KEY (LessonID) REFERENCES Lessons (LessonID));''',
        '''CREATE TABLE IF NOT EXISTS UserProgress (ProgressID INTEGER PRIMARY KEY, UserID INTEGER, LessonID INTEGER, CompletionDate DATE, QuizScore INTEGER, FOREIGN KEY (UserID) REFERENCES Users (UserID), FOREIGN KEY (LessonID) REFERENCES Lessons (LessonID));'''
    ]

    # Execute the commands to create tables
    for command in create_table_commands:
        cursor.execute(command)

    # Commit and close
    conn.commit()
    conn.close()

# Initialize the database and tables
if __name__ == "__main__":
    create_tables()
    print("Database and tables are set up.")
