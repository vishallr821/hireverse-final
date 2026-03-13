from jobs.models import JobDescription
from resumes.models import Candidate
from .models import RankingResult
from .similarity import rank_all_candidates, get_top_n
from .llm_scorer import score_candidate
from django.db import transaction

def run_ranking_pipeline(job_id: int) -> list:
    """Executes the full ranking pipeline for a specific job."""
    # Step 1: Get Job
    try:
        job = JobDescription.objects.get(id=job_id)
    except JobDescription.DoesNotExist:
        raise ValueError(f"Job with ID {job_id} not found.")

    if not job.embedding or len(job.embedding) == 0:
        print(f"Job '{job.title}' has no embedding, generating on the fly...")
        from resumes.embedder import embed_job_description
        job.embedding = embed_job_description(
            job.title, 
            job.description, 
            job.required_skills
        )
        job.save()
        print(f"Job embedding generated: {len(job.embedding)} dims")

    # Step 2: Get Candidates (processing missing embeddings on the fly)
    all_candidates = Candidate.objects.all()
    candidates_list = []
    
    from resumes.embedder import embed_resume
    for c in all_candidates:
        if not c.embedding or len(c.embedding) == 0:
            print(f"Candidate {c.name} has no embedding, generating...")
            c.embedding = embed_resume(c.raw_text, c.parsed_skills)
            if c.embedding:
                c.chroma_id = f"candidate_{c.id}"
                c.save()
                print(f"  Done! {len(c.embedding)} dims")
            else:
                print(f"  FAILED to generate embedding for {c.name}, skipping.")
                continue
        
        candidates_list.append({
            'candidate_id': c.id,
            'name': c.name,
            'embedding': c.embedding
        })

    # Step 4: Handle empty candidates
    if not candidates_list:
        return []

    # Step 5: Rank by Cosine Similarity
    ranked_results = rank_all_candidates(job.embedding, candidates_list)

    # Step 6: Top 10 for detailed LLM scoring
    top_10_list = get_top_n(ranked_results, 10)

    # Step 7 & Additional: LLM Scoring and Metadata Persistence
    final_rankings = []
    with transaction.atomic():
        processed_ids = []
        for index, res in enumerate(top_10_list):
            candidate = Candidate.objects.get(id=res['candidate_id'])
            cosine_score = res['cosine_score']
            
            print(f"LLM Scoring for candidate: {candidate.name}")
            # Call LLM scorer
            llm_result = score_candidate(
                job_title=job.title,
                job_description=job.description,
                required_skills=job.required_skills,
                resume_text=candidate.raw_text[:2000],
                candidate_skills=candidate.parsed_skills
            )
            
            # Calculate final score: (cosine_score * 40) + (llm_score * 0.6)
            final_score = round((cosine_score * 40) + (llm_result['score'] * 0.6), 2)
            
            ranking_obj, created = RankingResult.objects.update_or_create(
                job=job,
                candidate=candidate,
                defaults={
                    'cosine_score': cosine_score,
                    'llm_score': llm_result['score'],
                    'final_score': final_score,
                    'seniority_level': llm_result['seniority_level'],
                    'strengths': llm_result['strengths'],
                    'skill_gaps': llm_result['skill_gaps'],
                    'recommendation': llm_result['recommendation'],
                    'reasoning': llm_result['reasoning'],
                    'rank_position': 0 # Will update after all are scored
                }
            )
            processed_ids.append(ranking_obj.id)
            print(f"Scored {candidate.name}: {llm_result['score']}/100 - {llm_result['recommendation']}")

        # Step 8: Clean old results
        RankingResult.objects.filter(job=job).exclude(id__in=processed_ids).delete()
        
        # Re-sort ALL results for this job by final_score and update rank_position
        results = RankingResult.objects.filter(job=job).order_by('-final_score')
        for i, ranking in enumerate(results):
            ranking.rank_position = i + 1
            ranking.save()
            final_rankings.append(ranking)

    return final_rankings
