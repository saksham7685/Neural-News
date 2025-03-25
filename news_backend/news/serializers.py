from rest_framework import serializers
from .models import NewsArticle, NewsSummary

class NewsArticleSerializer(serializers.ModelSerializer):
    overview = serializers.SerializerMethodField()
    published_at = serializers.DateTimeField(format="%Y-%m-%d") 
    class Meta:
        model = NewsArticle
        fields = ["title", "overview", "source", "url", "credibility_score", "bias_score","published_at","genres"]

    def get_overview(self, obj):
        
        words = obj.content.split()  # Split content into words
        if len(words) > 150:
            return " ".join(words[:150]) + "..."
        return obj.content

class NewsSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsSummary
        fields = ['app_id', 'genres_selected', 'summary', 'published_at']