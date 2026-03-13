from django.contrib import admin
from .models import RankingResult

@admin.register(RankingResult)
class RankingResultAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'rank_position', 'final_score')
    list_filter = ('job',)
