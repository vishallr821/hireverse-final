from django.db import models
from django.conf import settings

class JobDescription(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField(blank=True)
    chroma_id = models.CharField(max_length=200, blank=True)
    embedding = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    @property
    def required_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def __str__(self):
        return self.title
