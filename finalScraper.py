from urllib.parse import quote

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import sqlite3
import os

flaresolverr = 'http://localhost:8191/v1'


def scrape_website_selenium(url):
    try:
        # Specify the path to your chromedriver
        driver = webdriver.Chrome()
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "c-card__title"))
        )

        # Get the page source
        page_source = driver.page_source

        return page_source

    except TimeoutException:
        print("Timeout: The page took too long to load.")
        return None

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return None

    finally:
        # Close the browser in the final block
        if driver:
            driver.quit()

def parse_articles(page_source):
    # Use BeautifulSoup to parse the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Use a list to store articles
    articles = {}

    base_url = "https://www.bassresource.com"

    # Use a list comprehension for conciseness
    article_cards = soup.find_all('a', class_='c-card c-card--raised')

    for card in article_cards:
        # Use try-except to handle missing attributes
        try:
            title = card.find('h3', class_='c-card__title').text.strip()
            link = card['href']

            # Prepend base URL if links are relative
            full_link = f"{base_url}{link}" if not link.startswith('http') else link

            # Append a dictionary to the list
            articles.update({title: full_link})

        except (AttributeError, KeyError) as e:
            print(f"Error extracting article: {e}")
    print(articles)
    return articles


def proxy_request_and_scrape(articles):
    title_content = {}
    for url in articles:
        payload = {
            "cmd": "request.get",
            "url": articles[url],
            "maxTimeout": 60000
        }
        print(f"Scraping article content from: {url}")
        try:
            response = requests.post(flaresolverr, json=payload)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

            json_response = response.json()

            if json_response.get('status') == 'ok':
                html = json_response.get('solution', {}).get('response', None)
                print('Success')
                soup = BeautifulSoup(html, 'html.parser')
                content_div = soup.find('div', {"property": "schema:text", "itemprop": "articleBody"})
                title_content[url] = content_div.text.strip() if content_div else None

        except requests.RequestException as req_ex:
            print(f"Request error: {req_ex}")
        except Exception as ex:
            print(f"An error occurred while processing the response: {ex}")

    return title_content


def create_database_table():
    try:
        conn = sqlite3.connect('fishing_course.db')
        c = conn.cursor()

        # Create table if it does not exist
        c.execute('''CREATE TABLE IF NOT EXISTS articles
                     (title TEXT, content TEXT)''')

        # Save (commit) the changes
        conn.commit()
        print("Database table created successfully.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the connection
        conn.close()


def store_data(article_data):
    try:
        title_encoded = quote(article_data['title'], safe='')

        conn = sqlite3.connect('fishing_course.db')
        c = conn.cursor()

        # Insert a row of data
        c.execute("INSERT INTO articles (title, content) VALUES (?, ?)",
                  (title_encoded, article_data['content']))

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

        # Create database table if not exists
        create_database_table()

        website_url = "https://www.bassresource.com/how-to-fish"
        page_source = scrape_website_selenium(website_url)

        if page_source:
            articles = parse_articles(page_source)

            print(f"Found {len(articles)} articles.")
            if articles:
                content = proxy_request_and_scrape(articles)

                for title, url in articles.items():
                    if title in content:
                        article_data = {'title': title, 'content': content.get(title)}
                        store_data(article_data)
            else:
                print("No articles to process.")

    except Exception as e:
        print(f"An error occurred: {e}")

    print("Script finished.")