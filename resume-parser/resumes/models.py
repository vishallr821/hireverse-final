from django.db import models
from django.conf import settings

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    raw_text = models.TextField()
    parsed_skills = models.JSONField(default=list)
    embedding = models.JSONField(null=True, blank=True)
    chroma_id = models.CharField(max_length=200, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
