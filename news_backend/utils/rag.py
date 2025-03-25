import os
import sys
import django
import torch
import logging
import gc
from langchain.chains import RetrievalQA
from langchain_pinecone import PineconeVectorStore
from langchain_community.llms import Ollama
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate

DJANGO_PROJECT_PATH = r"C:\Users\91741\news_backend"
sys.path.insert(0, DJANGO_PROJECT_PATH)  
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_backend.settings")
django.setup()

from utils.embeddings import retrieve_relevant_news  
from news.models import NewsArticle


os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

torch.cuda.empty_cache()
torch.cuda.reset_max_memory_allocated()
torch.cuda.reset_max_memory_cached()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "**********************")  
PINECONE_ENV = "us-east-1"
pc = Pinecone(api_key=PINECONE_API_KEY)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    torch.backends.cudnn.benchmark = True  
    torch.cuda.set_per_process_memory_fraction(0.9, 0) 
    logging.info("using gpu!!")
else:
    logging.warning("runnning on cpu")


model_path = r"C:\Users\91741\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2\snapshots\c9745ed1d9f207416be6d2e6f8de32d1f16199bf"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": device}
)


# 🔹 Initialize Pinecone Vector Store
vector_store = PineconeVectorStore(
    index_name="news-embeddings",
    embedding=embedding_model,
    pinecone_api_key=PINECONE_API_KEY
)

try:
    llm = Ollama(model="zephyr-7b-alpha", temperature=0.7, verbose=True)
    
    logging.info("✅ Zephyr 7B (Ollama) model loaded successfully.")

except Exception as e:
    logging.error(f"❌ Failed to load Ollama model: {e}")
    exit(1)

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k":2} )


qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
)
def answer_user_query(user_query, documents):
    torch.cuda.empty_cache()
    gc.collect()

    # Store docs in vector store 
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})

    # Retrieve relevant documents

    retrieved_docs = retriever.invoke(user_query)

    for i, doc in enumerate(retrieved_docs):
        print(f"\n🔍 Document {i+1}:")
        print("Metadata:", doc.metadata)  # Print available metadata
        print("Text:", getattr(doc, "page_content", "No text found"))

    # Extract content from metadata 
    context = " ".join([
    doc.metadata.get("Text", "")
    for doc in retrieved_docs
    if doc.metadata.get("Text")
    ])


    # passing context LLM for response generation
    result = qa_chain.invoke({"query": user_query, "context": context})

    # final response
    sources = [
        {
            "title": doc.metadata.get("title", "Unknown"),
            "published_at": doc.metadata.get("published_at", "Unknown"),
            "source": doc.metadata.get("source", "Unknown"),
        }
        for doc in retrieved_docs
    ]

    return {
        "query": user_query,
        "answer":{ "result":result.get("result", "No answer generated.")},
        "retrieved_sources": sources,
    }

