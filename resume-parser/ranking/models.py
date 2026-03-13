from django.db import models

class RankingResult(models.Model):
    job = models.ForeignKey('jobs.JobDescription', on_delete=models.CASCADE, related_name='rankings')
    candidate = models.ForeignKey('resumes.Candidate', on_delete=models.CASCADE, related_name='rankings')
    cosine_score = models.FloatField(default=0.0)
    llm_score = models.IntegerField(null=True, blank=True)
    final_score = models.FloatField(default=0.0)
    rank_position = models.IntegerField(default=0)
    seniority_level = models.CharField(max_length=50, blank=True)
    strengths = models.JSONField(default=list)
    skill_gaps = models.JSONField(default=list)
    recommendation = models.CharField(max_length=50, blank=True)
    reasoning = models.TextField(blank=True)
    ranked_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rank_position']
        unique_together = [['job', 'candidate']]

    def __str__(self):
        return f"{self.candidate.name} - {self.job.title} Rank: {self.rank_position}"
