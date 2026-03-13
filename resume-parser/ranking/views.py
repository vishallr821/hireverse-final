from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .pipeline import run_ranking_pipeline
from jobs.models import JobDescription


@require_POST
def trigger_ranking(request, pk):
    """View to trigger the ranking pipeline for a job."""
    try:
        run_ranking_pipeline(pk)
        messages.success(request, "Candidate ranking completed successfully.")
    except Exception as e:
        messages.error(request, f"Ranking error: {str(e)}")
    
    return redirect('ranking:ranking_results', pk=pk)


def ranking_results(request, pk):
    """View to display the full ranking results for a job."""
    job = get_object_or_404(JobDescription, pk=pk)
    rankings = job.rankings.all().order_by('rank_position')
    
    # Calculate some summary stats
    top_score = rankings.first().final_score if rankings.exists() else 0
    avg_score = sum(r.final_score for r in rankings) / rankings.count() if rankings.exists() else 0
    
    context = {
        'job': job,
        'rankings': rankings,
        'candidate_count': rankings.count(),
        'top_score': top_score,
        'avg_score': avg_score,
    }
    return render(request, 'ranking/ranking_results.html', context)
