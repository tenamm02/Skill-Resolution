import sqlite3

def store_data(article_data):
    try:
        print(f"Storing data for article: {article_data['title']}")
        conn = sqlite3.connect('fishing_course.db')
        c = conn.cursor()

        # Create table if it does not exist
        c.execute('''CREATE TABLE IF NOT EXISTS articles
                     (title TEXT UNIQUE, content TEXT)''')

        # Check if the article already exists
        c.execute("SELECT title FROM articles WHERE title = ?", (article_data['title'],))
        if c.fetchone() is None:
            # If not, insert the new article
            c.execute("INSERT INTO articles (title, content) VALUES (?, ?)",
                      (article_data['title'], article_data['content']))
            conn.commit()
            print("Data stored successfully.")
        else:
            print(f"Article already exists: {article_data['title']}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the connection
        conn.close()
