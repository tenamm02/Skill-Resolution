import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article_cards = soup.find_all('a', class_='c-card c-card--raised')
    return [(card.find('h3', class_='c-card__title').text.strip(), card['href']) for card in article_cards]

def scrape_article_content(article_url):
    base_url = "https://www.bassresource.com"
    response = requests.get(base_url + article_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Targeting the div with the article content using the attributes
    content_div = soup.find('div', {"property": "schema:text", "itemprop": "articleBody"})
    
    return content_div.text.strip() if content_div else None


client = MongoClient('localhost', 27017)
db = client.FishingCourse
articles_collection = db.articles

def store_data(article_data):
    articles_collection.insert_one(article_data)

if __name__ == "__main__":
    website_url = "https://www.bassresource.com/how-to-fish"
    articles = scrape_website(website_url)
    
    for title, url in articles:
        content = scrape_article_content(url)
        article_data = {
            "title": title,
            "content": content
        }
        store_data(article_data)
