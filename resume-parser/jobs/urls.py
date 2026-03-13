from django.urls import path
from . import views
from ranking.views import trigger_ranking

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('create/', views.job_create, name='job_create'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('<int:pk>/rank/', trigger_ranking, name='trigger_ranking'),
]
