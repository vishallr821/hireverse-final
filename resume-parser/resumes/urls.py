from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/<int:pk>/', views.candidate_detail, name='candidate_detail'),
]
