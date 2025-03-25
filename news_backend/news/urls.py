from django.urls import path
from .views import GetNewsView,TriggerScraperView ,GetNewsSummaryView ,QueryNewsView

urlpatterns = [
    path("trigger-scraper/", TriggerScraperView.as_view(), name="trigger_scraper"),
    path("get-news/", GetNewsView.as_view(), name="get_news"),
    path("get-Summary/", GetNewsSummaryView.as_view(), name="get_Summary"),
    path("query/", QueryNewsView.as_view(), name="query_news"),
]

