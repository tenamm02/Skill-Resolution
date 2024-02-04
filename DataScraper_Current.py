from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import sqlite3
import os
import time
import random

# Set up the Selenium WebDriver with Service
def scrape_website_selenium(url, user_agent):
    options = Options()
    options.add_argument(f"user-agent={user_agent}")  # Use the passed user_agent
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    
    service = Service(r'D:\GitHub\Skill-Resolution\chromedriver-win64\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "c-card__title")))
    page_source = driver.page_source
    driver.quit()
    
    return page_source



def parse_articles(page_source):
    # Use BeautifulSoup to parse the page source
    soup = BeautifulSoup(page_source, 'html.parser')
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

def scrape_article_content(article_url, driver):  # Add 'driver' as an argument
    print(f"Scraping article content from: {article_url}")
    driver.get(article_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[property='schema:text'][itemprop='articleBody']"))
    )
    content = driver.find_element(By.CSS_SELECTOR, "div[property='schema:text'][itemprop='articleBody']").text
    return content

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
    driver = None
    try:
        print("Script started.")
        ua = UserAgent()
        user_agent = ua.random
        website_url = "https://www.bassresource.com/how-to-fish"
        page_source = scrape_website_selenium(website_url, user_agent)
        articles = parse_articles(page_source)
        service = Service(r'D:\GitHub\Skill-Resolution\chromedriver-win64\chromedriver.exe')
        options = Options()
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Chrome(service=service, options=options)

        print(f"Found {len(articles)} articles.")
        if not articles:
            print("No articles to process.")

        for title, url in articles:
            try:
                print(f"Scraping article: {title}")
                content = scrape_article_content(url, driver)
                if content:  # Only proceed if content is not None or empty
                    article_data = {
                        "title": title,
                        "content": content
                    }
                    store_data(article_data)
                else:
                    print(f"No content found for article: {title}")
                time.sleep(random.uniform(40, 60))  # Randomize request intervals
            except Exception as e:
                print(f"An error occurred while processing the article '{title}' at URL '{url}': {e}")

        driver.quit()  # Close the driver after all articles are processed

    except Exception as e:
        print(f"An error occurred: {e}")
        if driver:
            driver.quit()  # Ensure the driver is closed in case of an error

    print("Script finished.")