from requests_html import HTMLSession
from bs4 import BeautifulSoup
import sqlite3
import time
import random

def scrape_website(url):
    session = HTMLSession()
    r = session.get(url)
    r.html.render(sleep=1, keep_page=True, timeout=20)  # Wait for JavaScript to execute
    return r.html.html

def parse_articles(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    article_cards = soup.find_all('a', class_='c-card c-card--raised')
    articles = []
    base_url = "https://www.bassresource.com"
    for card in article_cards:
        title = card.find('h3', class_='c-card__title').text.strip()
        link = card['href']
        full_link = f"{base_url}{link}"
        articles.append((title, full_link))
    return articles

def scrape_article_content(article_url):
    session = HTMLSession()
    r = session.get(article_url)
    r.html.render(sleep=1, keep_page=True, timeout=20)
    content = r.html.find("div[property='schema:text'][itemprop='articleBody']", first=True)
    return content.text if content else None

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
        website_url = "https://www.bassresource.com/how-to-fish"
        html_content = scrape_website(website_url)
        articles = parse_articles(html_content)

        print(f"Found {len(articles)} articles.")
        if not articles:
            print("No articles to process.")

        for title, link in articles:
            print(f"Scraping article: {title}")
            content = scrape_article_content(link)
            if content:
                article_data = {"title": title, "content": content}
                store_data(article_data)
            else:
                print(f"No content found for article: {title}")
            time.sleep(random.uniform(5, 10))  # Randomize request intervals
    except Exception as e:
        print(f"An error occurred: {e}")
    print("Script finished.")
