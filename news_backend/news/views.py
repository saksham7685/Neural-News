from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import NewsArticle ,NewsSummary
from rest_framework.views import APIView
from .serializers import NewsArticleSerializer
from user.models import User
from django.db.models import Max
import os
import re
import sys
import django
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from django.db.models.functions import TruncDate
from collections import defaultdict
from utils.rag import answer_user_query
from utils.embeddings import retrieve_relevant_news

 # Adjust import based on your Scrapy project structure

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_backend.settings")
django.setup()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Adds the directory containing views.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "news_scraper")))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
import threading
from news_scraper.spiders.scraper import NewsSpider 
from rest_framework_simplejwt.tokens import AccessToken

class TriggerScraperView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def run_scraper(self, user_email):
        
        process = CrawlerProcess(get_project_settings())
        process.crawl(NewsSpider, email=user_email)  # Pass the user's email
        process.start(stop_after_crawl=False)

    def get(self, request):
        

        print("===== Debugging Authentication =====")
        print(f"Raw Request User: {request.user}")
        print(f"User Authenticated: {request.user.is_authenticated}")
        print(f"User UUID: {getattr(request.user, 'uuid', 'Missing')}")
        print(f"Auth Object: {getattr(request, 'auth', None)}")
        print("====================================")

        if request.user.is_authenticated:
            # Extract the UUID from the authenticated user (JWT payload)
            user_uuid = request.user.uuid  # DRF maps `user_id` to `request.user.id`

            # Look up the user in the database using the UUID
            try:
                user_instance = User.objects.get(uuid=user_uuid)
                user_email = user_instance.email
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404)

            # Extract the email from the database
            #user_email = user_instance.email

            # Run Scrapy in a separate process using the found email
            threading.Thread(target=self.run_scraper, args=(user_email,)).start()


            return JsonResponse({"message": "Scraper started successfully!"})
        
       

        return JsonResponse({"error": "User not authenticated"}, status=401)



class GetNewsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request,genre=None):
        user = request.user
        app_id = user.app_id

        print(f"User: {request.user}, App ID: {user.app_id}")

        # Base filter criteria
        filter_criteria = {"app_id": app_id}

        # Fetch all news articles for the user's app_id
        news_articles = NewsArticle.objects.filter(**filter_criteria)

        # If genre is provided, filter by genre
        if genre:
            genres_list = [g.strip().lower() for g in genre.split(",")]
            q_objects = Q()
            for g in genres_list:
                q_objects |= Q(genres__iexact=g)  # Case-insensitive exact match for strings

            news_articles = news_articles.filter(q_objects)
            print(f"Filtering for genres: {genres_list}")

        print(f"Fetched {news_articles.count()} articles for app_id {app_id}")

        if not news_articles.exists():
            return Response({"message": "News not found"}, status=404)

        # Find the latest date (ignoring time) using TruncDate
        latest_date = (
            news_articles.annotate(date=TruncDate("published_at"))
            .order_by("-date")
            .values_list("date", flat=True)
            .first()
        )
        print(f"Latest Date: {latest_date}")

        # Filter by the latest date (ignoring time) and order by newest creation
        latest_news_articles = (
            news_articles.annotate(date=TruncDate("published_at"))
            .filter(date=latest_date)
            .order_by("-created_at")
        )

        serializer = NewsArticleSerializer(latest_news_articles, many=True)
        return Response(serializer.data, status=200)


class GetNewsSummaryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        app_id = user.app_id  # Ensure app_id exists in the User model

        # Fetch the latest news for the user's app_id
        latest_news = NewsSummary.objects.filter(app_id=app_id).order_by('-published_at').values(
            'app_id', 'genres_selected', 'summary', 'published_at'
        ).first()

        if latest_news:
            # Extract category and clean summary
            cleaned_summary = []
            for line in latest_news["summary"].split("\n\n"):  # Split into sections
                match = re.match(r"\[\[(.*?)\]\]\n(.*)", line, re.DOTALL)
                if match:
                    category = match.group(1)  # Extract category name (e.g., "Sports")
                    text = match.group(2).strip().replace("\n", "<br>")  # Replace \n with <br> for formatting
                    cleaned_summary.append(f"{category}: {text}")  # Keep category, format nicely
                else:
                    cleaned_summary.append(line.strip().replace("\n", "<br>"))  # Apply <br> globally

            formatted_summary = " ".join(cleaned_summary)  # Join cleaned sections back

            return Response({
                "app_id": latest_news["app_id"],
                "genres_selected": latest_news["genres_selected"],  # Keeping genres as is
                "summary": formatted_summary,  # Properly formatted summary with visible line breaks
                "published_at": latest_news["published_at"]
            }, status=200)
        else:
            return Response({"message": "No news found for this app_id"}, status=404)

class QueryNewsView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user  
        user_app_id = user.app_id  

        user_query = request.data.get("query")
        if not user_query:
            return Response({"error": "Query is required"}, status=400)

        # ✅ Step 1: Retrieve news articles for the user
        news_articles = NewsArticle.objects.filter(app_id=user_app_id)

        # ✅ Step 2: Get the latest news date
        latest_date = (
            news_articles.annotate(date=TruncDate("published_at"))
            .order_by("-date")
            .values_list("date", flat=True)
            .first()
        )

        if not latest_date:
            return Response({"query": user_query, "answer": "No news available for your profile."})

        # ✅ Step 3: Get articles from the latest date
        latest_news_articles = news_articles.annotate(date=TruncDate("published_at")).filter(date=latest_date)

        if not latest_news_articles.exists():
            return Response({"query": user_query, "answer": "No relevant news found for the latest day."})

        # ✅ Step 4: Format documents with metadata for RAG retrieval
        documents = [
            {
                "content": article.content,
                "metadata": {
                    "app_id": str(article.app_id),
                    "title": article.title,
                    "published_at": article.published_at.strftime("%Y-%m-%d"),
                    "source": article.source,
                    "genre": article.genres,
                },
            }
            for article in latest_news_articles
        ]

        # ✅ Step 5: Generate an answer using the modified RAG function
        response_data = answer_user_query(user_query, documents)

        return Response(response_data)
