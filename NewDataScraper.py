import requests
from bs4 import BeautifulSoup
import sqlite3
import os

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all article cards
    article_cards = soup.find_all('a', class_='c-card c-card--raised')
    
    # Extract title and link from each card
    articles = []
    base_url = "https://www.bassresource.com"
    for card in article_cards:
        title = card.find('h3', class_='c-card__title').text.strip()
        link = card['href']
        full_link = f"{base_url}{link}"  # Prepend base URL if links are relative
        articles.append((title, full_link))
    
    return articles

def scrape_article_content(article_url):
    print(f"Scraping article content from: {article_url}")
    base_url = "https://www.bassresource.com"
    response = requests.get(base_url + article_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    content_div = soup.find('div', {"property": "schema:text", "itemprop": "articleBody"})
    return content_div.text.strip() if content_div else None

def store_data(article_data):
    try:
        print(f"Storing data for article: {article_data['title']}")
        conn = sqlite3.connect('fishing_course.db')
        c = conn.cursor()

        # Create table if it does not exist
        c.execute('''CREATE TABLE IF NOT EXISTS articles
                     (title TEXT, content TEXT)''')

        # Insert a row of data
        c.execute("INSERT INTO articles (title, content) VALUES (?, ?)",
                  (article_data['title'], article_data['content']))

        # Save (commit) the changes
        conn.commit()
        print("Data stored successfully.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    try:
        print("Script started.")
        print(f"Current working directory: {os.getcwd()}")
        website_url = "https://www.bassresource.com/how-to-fish"
        articles = scrape_website(website_url)
        
        print(f"Found {len(articles)} articles.")
        if not articles:
            print("No articles to process.")

        for title, url in articles:
            print(f"Scraping article: {title}")
            content = scrape_article_content(url)
            article_data = {
                "title": title,
                "content": content
            }
            store_data(article_data)
    
    except Exception as e:
        print(f"An error occurred: {e}")

    print("Script finished.")