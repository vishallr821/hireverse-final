from django.urls import path
from . import views

app_name = 'ranking'
urlpatterns = [
    path('results/<int:pk>/', views.ranking_results, name='ranking_results'),
]
