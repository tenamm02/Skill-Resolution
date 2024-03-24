import sqlite3

# Connect to the SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect('D:\\GitHub\\Skill-Resolution\\course_platform.db')

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Function to insert a new user into the Users table
def insert_user(username, useremail, registrationdate):
    cursor.execute('''INSERT INTO Users (UserName, UserEmail, RegistrationDate) VALUES (?, ?, ?)''', (username, useremail, registrationdate))
    conn.commit()

# Function to fetch and print all users from the Users table
def fetch_all_users():
    cursor.execute('''SELECT * FROM Users''')
    for row in cursor.fetchall():
        print(row)

# Insert a new user
insert_user('testuser1', 'test1@example.com', '2024-01-30')

# Fetch and print all users
fetch_all_users()

# Close the database connection
conn.close()