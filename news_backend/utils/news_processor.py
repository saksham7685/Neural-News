import re
import spacy
import nltk
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from summa import summarizer 
from news.models import NewsArticle ,NewsSummary
from user.models import User


nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
   
    text = re.sub(r'\s+', ' ', text)  
    return text.strip()

def remove_extra_spaces(text):
    pattern = r'(?<=\s)(\w)(\s+)(\w)(?=\s)'
    

    if re.search(pattern, text):
        chars = [c for c in text if c.strip()]
        words = ''.join(chars).split()
        return ' '.join(words)   
    return text

def extractive_summary(text, max_sentences=1):

    summarized= summarizer.summarize(text, ratio=0.05)  
    sentences = nltk.sent_tokenize(summarized)
    
    if len(sentences) > max_sentences:
        sentences = sentences[:max_sentences] 

    return " ".join(sentences)


def tfidf_summary(text, max_sentences=2):
   
    sentences = nltk.sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(sentences)
    scores = X.sum(axis=1).A1  
    ranked_sentences = [sentences[i] for i in scores.argsort()[-max_sentences:]]
    return " ".join(ranked_sentences)


def limit_words(summary, max_words=100):
    sentences = nltk.sent_tokenize(summary)  
    result = []
    word_count = 0

    for sentence in sentences:
        words_in_sentence = len(sentence.split())

        if word_count + words_in_sentence > max_words:
            break  

        result.append(sentence)
        word_count += words_in_sentence

    return " ".join(result) 

def generate_news_summaries():
    summaries = defaultdict(lambda: defaultdict(str))
    articles = NewsArticle.objects.values("app_id", "published_at", "content", "genres").order_by("published_at")

    for article in articles:
        key = (article["app_id"], article["published_at"].date())

        cleaned_text = preprocess_text(article["content"])
        extracted_summary = extractive_summary(cleaned_text)
        tfidf_based_summary = tfidf_summary(cleaned_text)

        final_summary = tfidf_based_summary if extracted_summary in tfidf_based_summary else extracted_summary + " " + tfidf_based_summary
        limited_summary = limit_words(final_summary)

        
        for g in article["genres"]:  
            summaries[key][g] += f"\n{limited_summary} "

    for (app_id, published_at), genre_dict in summaries.items():
        user = User.objects.filter(app_id=app_id).first()
        if user:
            # Convert `genre_dict` to a properly formatted string
            formatted_summary = "\n\n".join(f"<br><br><strong>{genre.upper()}</strong>:<br>{text.strip()}" for genre, text in genre_dict.items()).strip()

            NewsSummary.objects.update_or_create(
                app_id=user,
                published_at=published_at,
                defaults={
                    "name": user.name,
                    "email": user.email,
                    "genres_selected": user.genres_selected,
                    "summary": formatted_summary,  # Fixed formatting issue
                }
            )

    print("✅ News summaries generated successfully.")
