import os
import django
import scrapy
import sys
import re
import numpy as np
from datetime import datetime
from selenium import webdriver
from scrapy.selector import Selector
from sentence_transformers import SentenceTransformer

# ✅ Setup Django
DJANGO_PROJECT_PATH = r"C:\Users\91741\news_backend"
sys.path.insert(0, DJANGO_PROJECT_PATH)  
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_backend.settings")
django.setup()

from news.models import NewsArticle  
from user.models import User 
from utils.news_processor import generate_news_summaries  
from utils.credibility import get_credibility_score
from utils.bias import get_bias_score
from utils.embeddings import store_news_in_pinecone



model = SentenceTransformer("all-MiniLM-L6-v2")

GENRE_EXAMPLES = {
    "Technology": "Latest gadgets, software, cybersecurity, digital trends, programming.",
    "Science": "Scientific discoveries, space exploration, physics, biology, chemistry.",
    "Politics": "Government policies, elections, president, ministers, state laws, international relations, democracy.",
    "Sports": "Football, cricket, Olympics, NBA, tennis, sports leagues and events.",
    "Entertainment": "Movies, TV shows, celebrities, Hollywood, Bollywood, entertainment industry.",
    "Business": "Stock market, economy, startups, investments, corporate trends, finance.",
    "Health": "Medical research, fitness, diseases, healthcare policies, nutrition.",
    "Education": "Education system, universities, exams, scholarships, learning techniques.",
    "Travel": "Travel destinations, tourism, adventure, travel tips, cultural experiences.",
    "Lifestyle": "Fashion, trends, wellness, self-care, lifestyle tips, home decor.",
    "Astrology": "Horoscopes, zodiac signs, celestial influences, personality traits, cosmic predictions.",
    "Gaming": "Video games, esports, gaming industry trends, reviews, game development.",
    "Finance": "Banking, personal finance, investments, stock market, financial policies.",
    "Music": "Artists, music industry, new releases, concerts, trends in music.",
    "Movies": "Film industry, Hollywood, Bollywood, movie reviews, award shows.",
    "Food": "Food trends, recipes, restaurant reviews, culinary innovations, health foods.",
    "Artificial Intelligence": "AI advancements, machine learning, deep learning, automation, neural networks.",
    "Climate & Environment": "Climate change, renewable energy, sustainability, environmental conservation.",
    "History & Culture": "Historical events, anthropology, cultural heritage, ancient civilizations.",
    "Social Issues": "Social justice, human rights, gender equality, activism, societal changes.",
    "Crime & Law": "Crime reports, criminal investigations, court cases, cybercrime, legal reforms.",
    "Automobiles": "Electric vehicles, car launches, automotive industry trends, road safety.",
    "Space": "Space missions, NASA, ISRO, exoplanets, cosmic discoveries, astronomy.",
    "Startups & Entrepreneurship": "Startup culture, venture capital, new business ideas, entrepreneurship.",
    "Economy": "Global economy, GDP trends, inflation, trade, financial markets.",
    "Psychology & Mental Health": "Mental health, psychology, therapy, stress management, behavioral science.",
    "Real Estate": "Housing market trends, property investments, urban development, real estate laws.",
    "Defense & Military": "Military updates, defense technology, global conflicts, war strategies.",
    "Cryptocurrency & Blockchain": "Bitcoin, Ethereum, NFTs, blockchain trends, Web3 innovations.",
    "Science Fiction & Futurism": "Futuristic technology, AI ethics, space colonization, sci-fi theories.",
    "Philosophy & Ethics": "Morality, ethics, philosophy of technology, existential debates."
}

# ✅ Compute genre embeddings
genre_embeddings = {genre: model.encode(text) for genre, text in GENRE_EXAMPLES.items()}

# ✅ Function to classify genre
def classify_genre(article_content):
    if not article_content:
        return "unknown"
    article_embedding = model.encode(article_content)
    similarities = {genre: np.dot(article_embedding, embedding) for genre, embedding in genre_embeddings.items()}
    return max(similarities, key=similarities.get)

class NewsSpider(scrapy.Spider):
    name = "news_scraper"

    news_sites = {
        "IndianExpress": "https://indianexpress.com/",
        "Hindustantimes": "https://www.hindustantimes.com",
    }

    def __init__(self, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        
        self.logger.info(f"🟡 kwargs received: {kwargs}")  

        email = kwargs.get("email")  
        self.logger.info(f"🟡 Extracted email: {email}")  

        if not email:
            self.logger.error("❌ No email provided to the spider!")
            self.user = None
            return  

        try:
            self.user = User.objects.get(email=email)
            self.logger.info(f"✅ Found user: {self.user.email}")  

            # ✅ Extract genres properly
            if isinstance(self.user.genres_selected, str):
                self.selected_genres = set(genre.strip().lower() for genre in self.user.genres_selected.split(","))
            else:
               self.selected_genres = set(genre.lower() for genre in self.user.genres_selected)


            self.logger.info(f"🎯 Selected Genres: {self.selected_genres}")

        except User.DoesNotExist:
            self.logger.error(f"❌ User with email {email} not found!")
            self.user = None
            self.selected_genres = set()

    def start_requests(self):
        sources = [
            {"url": "https://indianexpress.com/", "source": "IndianExpress", "priority": 1},
            {"url": "https://www.hindustantimes.com/", "source": "Hindustantimes", "priority": 2},
        ] 

        for site in sources:
            self.logger.info(f"🚀 Sending request to: {site['url']} (Source: {site['source']})")
            yield scrapy.Request(
                url=site["url"],
                callback=self.parse,
                meta={"source": site["source"]},
                priority=site["priority"],
            )

    def parse(self, response):
        """Parses article listings and sends requests to fetch full content"""
        self.logger.info(f"🔍 Parsing {response.url} from source: {response.meta['source']}")

        source = response.meta["source"]

        if source == "IndianExpress":
            articles = response.css("div.left-part > div.other-article")
            title_selector = "h3 > a::text"
            url_selector = "h3 > a::attr(href)"

        elif source == "Hindustantimes":
            articles = response.css("div.htImpressionTracking > div:nth-child(3)")
            title_selector = "a::text"
            url_selector = "a::attr(href)"
        else:
            return

        for article in articles:
            title = article.css(title_selector).get()
            url = article.css(url_selector).get()
            full_url = response.urljoin(url) if url else None

            if not full_url or not title:
                continue

            if source == "IndianExpress":
                # ✅ Send request to fetch full article content
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_indian_express_article,
                    meta={"title": title, "source": source, "url": full_url},
                    priority=3
                )
            else:
                content = self.get_hindustan_times_content(full_url) if full_url else "No content available"

                if not content or len(content.split()) < 10:
                    self.logger.info(f"⚠️ Skipping due to short content: {title}")
                    continue

                self.process_and_save_article(title, full_url, content, source)

    def parse_indian_express_article(self, response):
        """Extracts full content from Indian Express articles"""
        title = response.meta["title"]
        source = response.meta["source"]
        full_url = response.meta["url"]

        # ✅ Extract full content from the article page
        content = " ".join(response.css("#pcl-full-content p *::text").getall()).strip()

        if not content or len(content.split()) < 10:
            self.logger.info(f"⚠️ Skipping due to short content: {title} ({source}) - {full_url}")
            return

        self.process_and_save_article(title, full_url, content, source)

    def get_hindustan_times_content(self, url):
        """Fetches full article content from Hindustan Times using Selenium"""
        self.logger.info(f"🌍 Fetching full article from Hindustan Times: {url}")

        try:
            driver = webdriver.Chrome()
            driver.get(url)
            html = driver.page_source
            response = Selector(text=html)
            content = response.css("div.storyDetails.taboola-readmore > div.detail > p *::text").getall()
            driver.quit()

            full_content = " ".join(content).strip() if content else "No content available"
            self.logger.info(f"✅ Fetched {len(content)} paragraphs from Hindustan Times")
            return full_content
        except Exception as e:
            self.logger.error(f"❌ Error fetching Hindustan Times content: {str(e)}")
            return "No content available"

    def process_and_save_article(self, title, full_url, content, source):
       
        genre_predicted = classify_genre(content or title)
        self.logger.info(f"🔍 Predicted Genre: {genre_predicted} | Available Genres: {self.selected_genres}")

        if genre_predicted.lower() not in self.selected_genres:
            self.logger.info(f"🚫 Skipping non-matching article: {title}")
            return

        published_at = datetime.now()

        credibility_score = get_credibility_score(title, content, source)
        bias_score = get_bias_score(content)

        self.logger.info(f"✅ Matched Article: {title} | Genre: {genre_predicted}")
        self.logger.info(f"📊 Credibility Score: {credibility_score} | 🏳️ Bias Score: {bias_score}")
        if not NewsArticle.objects.filter(url=full_url).exists():
            news_article, created = NewsArticle.objects.get_or_create(
                app_id=self.user,
                title=title.strip(),
                url=full_url,
                content=content.strip(),
                source=source.capitalize(),
                published_at=published_at,
                genres=genre_predicted,
                credibility_score=credibility_score,
                bias_score=bias_score
            )
            self.logger.info(f"✅ Saved: {title} ({source}) - {full_url}")
        else:
            self.logger.info(f"🔄 Skipping duplicate: {title} ({source}) - {full_url}")

    def closed(self, reason):
        
        self.logger.info("✅ Scraping finished. Triggering news summary generation...")
        generate_news_summaries()

        self.logger.info("✅ and storing the news embeddings in pinecone...")
        store_news_in_pinecone()