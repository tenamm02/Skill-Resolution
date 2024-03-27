import sqlite3

# Connect to the database
conn = sqlite3.connect('quiz_database.db')
cursor = conn.cursor()

# Delete the options column
cursor.execute('''
    ALTER TABLE questions 
    ADD COLUMN topic text;
''')


# Commit the changes
conn.commit()

# Close the connection
conn.close()