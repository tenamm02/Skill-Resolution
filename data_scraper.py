import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    titles = soup.find_all('span', {'property': 'schema:name'})  # Modify this as per the website's structure
    return [title.text for title in titles]

client = MongoClient('localhost', 27017)
db = client.FishingCourse
articles = db.articles

def store_data(title_list):
    for title in title_list:
        article_data = {
            "title": title,
            # Add more fields as required
        }
        articles.insert_one(article_data)

if __name__ == "__main__":
    website_url = "https://www.bassresource.com/"  # This is an example. Replace with your chosen website.
    titles = scrape_website(website_url)
    store_data(titles)
