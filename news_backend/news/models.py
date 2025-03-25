from django.conf import settings
from django.db import models
import uuid
from user.models import User  # Import User model
  # Import available genres

class NewsArticle(models.Model):
    genres = models.JSONField(default=list)  # Ensure it remains a list

    def save(self, *args, **kwargs):
        if isinstance(self.genres, str):  # Prevent future issues
            self.genres = [self.genres]
        super().save(*args, **kwargs)

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    app_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True , to_field="app_id",db_column="app_id")  # TEMPORARILY OPTIONAL
    title = models.CharField(max_length=500)
    content = models.TextField()
    source = models.CharField(max_length=255)  
    url = models.URLField(unique=True)
    published_at = models.DateTimeField()
    credibility_score = models.FloatField(default=0.5)  
    bias_score = models.FloatField(default=0.5)  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "news_articles"

    def __str__(self):
        return self.title



class NewsSummary(models.Model):
    id = models.AutoField(primary_key=True)

    # Foreign Key to User model
    app_id = models.ForeignKey(User, on_delete=models.CASCADE, to_field="app_id", db_column="app_id")

    # Store user details for optimization
    name = models.CharField(max_length=255)  
    email = models.EmailField()  
    genres_selected = models.JSONField(default=list)  

    # Aggregated News details
    published_at = models.DateField()  # Grouping by date (YYYY-MM-DD)
    summary = models.TextField()  # Summary of all news articles for the user on the same date

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "news_summary"
        unique_together = ("app_id", "published_at")  # Ensure one summary per user per day

    def __str__(self):
        return f"Summary for {self.name} ({self.app_id.app_id}) on {self.published_at}"
