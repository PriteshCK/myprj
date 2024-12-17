from django.urls import path
from . import views

urlpatterns = [
    path('scrape/', views.scrape_api, name='scrape_api'),
]

