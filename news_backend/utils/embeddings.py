import pinecone
from sentence_transformers import SentenceTransformer
from django.db.models import Max
from langchain.embeddings import HuggingFaceEmbeddings
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
import torch
import numpy as np
import os
import django
import sys

DJANGO_PROJECT_PATH = r"C:\Users\91741\news_backend"
sys.path.insert(0, DJANGO_PROJECT_PATH)  
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_backend.settings")
django.setup()

from news.models import NewsArticle



PINECONE_API_KEY = os.getenv("PINECONE_API_KEY","***********")  # Ensure API key is set in env
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "news-embeddings"

if index_name not in pc.list_indexes().names():
    pc.create_index(index_name, dimension=384, metric="cosine",spec=ServerlessSpec(cloud="aws", region="us-east-1"))  # Adjust for embedding size

index = pc.Index(index_name)


device = "cuda" if torch.cuda.is_available() else "cpu"
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def store_news_in_pinecone():

    news_articles = NewsArticle.objects.all()
    vectors = []

    for article in news_articles:
        embedding = embedder.embed_documents([article.content])[0]

        vectors_data={
            "id": str(article.uuid),
            "values": embedding,
            "metadata": {
                "app_id": str(article.app_id),
                "title": article.title,
                "published_at": article.published_at.strftime("%Y-%m-%d"),
                "text": article.content,
                "source": article.source,
                "genre":article.genres
            }
        }

        print(f"📌 Storing vector: {vectors_data}")  # Debugging output
        vectors.append(vectors_data)

    if vectors:
        try:
            index.upsert([(v["id"], v["values"], v["metadata"]) for v in vectors])
            logging.info("✅ News stored in Pinecone!")
        except Exception as e:
            logging.error(f"❌ Failed to upsert vectors: {e}")
    else:
        logging.warning("❌ No vectors to upsert!")

    try:
        index_stats = index.describe_index_stats()
        logging.info(f"📌 Pinecone Index Stats: {index_stats}")
    except Exception as e:
        logging.error(f"❌ Failed to get index stats: {e}")

def retrieve_relevant_news(query, app_id):
    try:
        latest_datetime = NewsArticle.objects.filter(app_id=app_id).aggregate(latest_datetime=Max("published_at"))["latest_datetime"]

        if not latest_datetime:
            return []  # No news found

        latest_date = latest_datetime.date()

        # 🔹 Step 2: Generate CUDA-accelerated embedding for the query
        query_embedding = embedder.embed_query(query)
        print(f"🔍 Query Embedding Shape: {len(query_embedding)}")

        results = index.query(vector=query_embedding,top_k=10, include_metadata=True)
        print(f"📌 Raw Pinecone Matches: {results}")

        retrieved_uuids = []
        for match in results["matches"]:
            metadata = match["metadata"]
            metadata_date = datetime.strptime(metadata["published_at"], "%Y-%m-%d").date()

            print(f"Raw Pinecone Matches: {results['matches']}")


            if str(metadata["app_id"]) == str(app_id) and metadata_date == latest_date:
                retrieved_uuids.append(match.id)

        return retrieved_uuids

    except Exception as e:
        logging.error(f"❌ Error during retrieval: {e}")
        return []
