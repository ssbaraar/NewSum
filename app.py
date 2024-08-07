import asyncio
import hashlib
import json
import os
import time
from datetime import datetime
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from dotenv import load_dotenv
from openai import OpenAI
from sanic import Sanic
from sanic.log import logger
from sanic.response import json as json_response
from sanic.response import html



load_dotenv()

app = Sanic(__name__)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_default_openai_api_key")
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")

# Load article data
JSON_FILE = 'data.json'

# Ensure JSON file exists if not
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'w') as f:
        json.dump({
            "articles": [],
            "preferences": {"sources": [], "keywords": []},
            "read_later": []
        }, f, indent=4)

async def fetch_feed(session, source):
    try:
        async with session.get(source['rss']) as response:
            if response.status == 200:
                content = await response.text()
                feed = feedparser.parse(content)
                return source, feed
            else:
                logger.info(f"Failed to fetch feed for {source['name']}: HTTP {response.status}")
                return source, None
    except Exception as e:
        logger.error(f"Error fetching feed for {source['name']}: {str(e)}")
        return source, None

async def fetch_article_content(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                return content
            else:
                logger.info(f"Failed to fetch article content: HTTP {response.status}")
                return None
    except Exception as e:
        logger.error(f"Error fetching article content: {str(e)}")
        return None

async def scrape_sources(sources):
    logger.info("Starting scrape_sources")
    start_time = time.time()
    articles = []
    articles_hashes = set()

    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [fetch_feed(session, source) for source in sources]
        feed_results = await asyncio.gather(*tasks, return_exceptions=True)

        for source, feed in feed_results:
            if isinstance(feed, Exception):
                logger.info(f"Error fetching feed for {source['name']}: {str(feed)}")
                continue
            if feed:
                logger.info(f"Processing feed for {source['name']}")
                for entry in feed.entries:
                    url = entry.link
                    title = entry.title
                    article_hash = hashlib.md5((url + title).encode()).hexdigest()
                    if article_hash not in articles_hashes:
                        content_task = fetch_article_content(session, url)
                        content_result = await content_task
                        if content_result:
                            content = content_result
                            summary = generate_summary(content)
                            publication_date = extract_publication_date(entry, content)
                            article = {
                                "id": article_hash,
                                "url": url,
                                "title": title,
                                "summary": summary,
                                "publication_date": publication_date.isoformat(),
                                "source": source['name']
                            }
                            articles.append(article)
                            articles_hashes.add(article_hash)

    logger.info(f"scrape_sources completed in {time.time() - start_time:.2f} seconds")
    return articles

def generate_summary(content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                {"role": "user", "content": f"Please summarize the following article content in 2-3 sentences:\n\n{content[:4000]}"},
            ],
            max_tokens=150
        )
        summary = response.choices[0].message.content.strip()
        logger.info(f"Summary generated: {summary[:50]}...")
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return "Error generating summary"

def extract_publication_date(entry, html_content):
    if 'published_parsed' in entry:
        return datetime(*entry.published_parsed[:6])
    elif 'updated_parsed' in entry:
        return datetime(*entry.updated_parsed[:6])
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        meta_date = soup.find('meta', {'property': 'article:published_time'}) or \
                    soup.find('meta', {'name': 'DCTIME'}) or \
                    soup.find('meta', {'name': 'published'}) or \
                    soup.find('meta', {'name': 'created'})
        if meta_date:
            try:
                return date_parser.parse(meta_date['content'])
            except:
                pass
    return datetime.now()
def get_preferences():
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)
    return data['preferences']

def get_articles():
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)
    return data['articles']

def get_read_later():
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)
    return data['read_later']

def save_preferences(sources, keywords):
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)
    data['preferences']['sources'] = sources
    data['preferences']['keywords'] = keywords
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_to_read_later(article_id):
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)
    data['read_later'].append(article_id)
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def remove_from_read_later(article_id):
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)
    data['read_later'].remove(article_id)
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Load OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# List of websites and their RSS feeds
SOURCES = [
    {"name": "GreenBiz", "url": "https://www.greenbiz.com/", "rss": "https://rss.app/feeds/PfSPW1PZmIDrjC8u.xml"},
    {"name": "Green.Earth", "url": "https://www.green.earth", "rss": "https://rss.app/feeds/bovDvfqaIz2KoDdw.xml"},
    {"name": "Sustainable Brands", "url": "https://sustainablebrands.com/", "rss": "https://rss.app/feeds/qKjOEYXW4oEP6xYP.xml"},
    {"name": "Carbon Credits", "url": "https://carboncredits.com/", "rss": "https://rss.app/feeds/56HKOZAvi3Ym1tm7.xml"},
    {"name": "Triple Pundit", "url": "https://www.triplepundit.com/", "rss": "https://rss.app/feeds/uZLwiQhErv8b4yEK.xml"},
    {"name": "ESG Today", "url": "https://www.esgtoday.com/", "rss": "https://rss.app/feeds/K2enb0duBnv1BgXn.xml"},
    {"name": "CoinDesk", "url": "https://www.coindesk.com/", "rss": "https://rss.app/feeds/YqqGCKRoUgtzQxse.xml"},
    {"name": "Forbes", "url": "https://www.forbes.com/", "rss": "https://rss.app/feeds/AlOYwfMt50xeeAGX.xml"},
    {"name": "PR Web", "url": "https://www.prweb.com/releases/news-releases-list/", "rss": "https://rss.app/feeds/4zjgvZfHGaKwST6D.xml"}
]

# Predefined keywords
KEYWORDS = ["tokenization", "web3", "RWA", "AI", "Biodiversity", "nature based carbon credits"]

@app.route('/')
async def index(request):
    logger.info("INDEX")
    preferences = get_preferences()
    sources = preferences["sources"]
    keywords = preferences["keywords"]
    articles = get_articles()
    filtered_articles = [article for article in articles if article['source'] in sources and any(keyword.lower() in article['title'].lower() or keyword.lower() in article.get('summary', '').lower() for keyword in keywords)]
    return json_response({'sources': sources, 'keywords': keywords, 'summaries': filtered_articles})

@app.route('/save_preferences', methods=['POST'])
async def save_preferences(request):
    logger.info("SAVE_PREFERENCES")
    sources = request.json.get('sources', [])
    keywords = request.json.get('keywords', [])
    save_preferences(sources, keywords)
    await scrape_sources(sources)
    return json_response({"message": "Preferences saved"})

@app.route('/all_articles')
async def all_articles(request):
    logger.info("ALL_ARTICLES")
    preferences = get_preferences()
    sources = preferences["sources"]
    keywords = preferences["keywords"]
    articles = get_articles()
    filtered_articles = [article for article in articles if article['source'] in sources and any(keyword.lower() in article['title'].lower() or keyword.lower() in article.get('summary', '').lower() for keyword in keywords)]
    return json_response({'summaries': filtered_articles})

@app.route('/read_later')
async def read_later(request):
    logger.info("READ_LATER")
    articles = get_articles()
    read_later_ids = get_read_later()
    read_later_articles = [article for article in articles if article['id'] in read_later_ids]
    return json_response({'summaries': read_later_articles})

@app.route('/add_to_read_later', methods=['POST'])
async def add_to_read_later(request):
    logger.info("ADD_TO_READ_LATER")
    article_id = request.json.get('id')
    add_to_read_later(article_id)
    return json_response({"message": "Added to Read Later list"})

@app.route('/remove_from_read_later', methods=['POST'])
async def remove_from_read_later(request):
    logger.info("REMOVE_FROM_READ_LATER")
    article_id = request.json.get('id')
    remove_from_read_later(article_id)
    return json_response({"message": "Removed from Read Later list"})

@app.route('/index')
async def serve_html(request):
    with open('index.html', 'r') as f:
        content = f.read()
    return html(content)

if __name__ == '__main__':
    app.run(debug=True)