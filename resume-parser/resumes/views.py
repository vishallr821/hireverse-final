import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Count, Max
from .models import Candidate
from .parser import parse_resume
from .embedder import embed_resume
from vector_store.chroma_client import add_resume_embedding
from jobs.models import JobDescription
from ranking.models import RankingResult


def dashboard(request):
    """Main dashboard view aggregating key metrics."""
    total_candidates = Candidate.objects.count()
    total_jobs = JobDescription.objects.count()
    recent_candidates = Candidate.objects.all().order_by('-uploaded_at')[:5]
    
    # Active jobs with candidate counts
    active_jobs = JobDescription.objects.filter(is_active=True).annotate(
        candidate_count=Count('rankings')
    ).order_by('-created_at')[:5]
    
    # Top 5 rankings across all jobs by score
    top_rankings = RankingResult.objects.all().select_related(
        'candidate', 'job'
    ).order_by('-final_score')[:5]
    
    # Resumes ranked count
    resumes_ranked = RankingResult.objects.values('candidate').distinct().count()
    
    # Top score this week (dummy logic or simplified)
    top_score = RankingResult.objects.aggregate(Max('final_score'))['final_score__max'] or 0
    
    context = {
        'total_candidates': total_candidates,
        'total_jobs': total_jobs,
        'recent_candidates': recent_candidates,
        'active_jobs': active_jobs,
        'top_rankings': top_rankings,
        'resumes_ranked': resumes_ranked,
        'top_score': top_score,
    }
    return render(request, 'resumes/dashboard.html', context)


def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume_file'):
        resume_file = request.FILES['resume_file']
        
        # Simple validation for extensions
        ext = os.path.splitext(resume_file.name)[1].lower()
        if ext not in ['.pdf', '.docx']:
            messages.error(request, "Only .pdf and .docx files are supported.")
            return render(request, 'resumes/upload.html')

        # FIX 1: PREVENT DUPLICATE RESUME UPLOADS
        existing = Candidate.objects.filter(
            resume_file__endswith=resume_file.name
        ).first()
        if existing:
            messages.warning(request, f'Resume "{resume_file.name}" already uploaded as {existing.name}')
            return redirect('resumes:candidate_list')

        # Create candidate object first to get the ID and file path
        candidate = Candidate(
            uploaded_by=None,
            resume_file=resume_file
        )
        candidate.save() # Save to get the file on disk or at least the path

        try:
            # Parse the resume
            result = parse_resume(candidate.resume_file.path)
            
            # Update candidate with parsed data
            candidate.raw_text = result['raw_text']
            candidate.parsed_skills = result['skills']
            # FIX 3 & 4: Save extracted name, email, phone
            candidate.name = result.get('name', resume_file.name.split('.')[0])
            candidate.email = result.get('email', '')
            candidate.phone = result.get('phone', '')
            candidate.save()

            # Generate and add embedding to ChromaDB
            print(f"Generating embedding for {candidate.name}...")
            embedding = embed_resume(candidate.raw_text, candidate.parsed_skills)
            print(f"Embedding generated, length: {len(embedding)}")
            
            chroma_id = f"candidate_{candidate.id}"
            
            if embedding:
                try:
                    add_resume_embedding(
                        chroma_id=chroma_id,
                        embedding=embedding,
                        metadata={
                            'name': candidate.name,
                            'email': candidate.email or "",
                            'candidate_id': str(candidate.id)
                        }
                    )
                except Exception as ce:
                    print(f"ChromaDB addition failed (non-fatal): {ce}")
            else:
                print(f"WARNING: Empty embedding for {candidate.name}")

            # Save embedding and chroma_id back to candidate
            candidate.embedding = embedding
            candidate.chroma_id = chroma_id
            candidate.save()
            
            messages.success(request, f"Successfully parsed {candidate.name}. Found {len(candidate.parsed_skills)} skills and generated embedding.")
            return redirect('resumes:candidate_list')
        except Exception as e:
            messages.error(request, f"Error processing resume: {str(e)}")
            return render(request, 'resumes/upload.html')

    return render(request, 'resumes/upload.html')


def candidate_list(request):
    candidates = Candidate.objects.all().order_by('-uploaded_at')
    
    query = request.GET.get('q')
    if query:
        candidates = candidates.filter(name__icontains=query)
        
    return render(request, 'resumes/candidate_list.html', {'candidates': candidates, 'query': query})


def candidate_detail(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    rankings = candidate.rankings.all()
    return render(request, 'resumes/candidate_detail.html', {
        'candidate': candidate,
        'rankings': rankings
    })
