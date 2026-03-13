from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from resumes import views as views_resumes

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views_resumes.upload_resume, name='dashboard'),
    path('resumes/', include('resumes.urls')),
    path('jobs/', include('jobs.urls')),
    path('ranking/', include('ranking.urls')),
    path('tests/', include('tests.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
