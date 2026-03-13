from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobDescription
from resumes.embedder import embed_job_description
from vector_store.chroma_client import add_jd_embedding


def job_list(request):
    jobs = JobDescription.objects.all().order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})


def job_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        # Clean up required_skills to be comma-separated
        required_skills = request.POST.get('required_skills', '')
        if required_skills:
            # If user entered space-separated, we split and join with comma
            # but usually they enter comma-separated. Let's just normalize.
            skills_list = [s.strip() for s in required_skills.split(',') if s.strip()]
            required_skills = ", ".join(skills_list)
        
        job = JobDescription.objects.create(
            title=title,
            description=description,
            required_skills=required_skills,
            created_by=None
        )
        
        try:
            # Generate embedding
            print(f"Generating embedding for job: {title}...")
            embedding = embed_job_description(title, description, required_skills)
            print(f"Job embedding generated, length: {len(embedding)}")
            
            chroma_id = f"jd_{job.id}"
            
            if embedding:
                # Add to ChromaDB
                try:
                    add_jd_embedding(
                        chroma_id=chroma_id,
                        embedding=embedding,
                        metadata={
                            'title': title,
                            'job_id': str(job.id)
                        }
                    )
                except Exception as ce:
                    print(f"ChromaDB JD addition failed (non-fatal): {ce}")
            
            # Save back to job
            job.chroma_id = chroma_id
            job.embedding = embedding
            job.save()
            
            messages.success(request, f"Job '{title}' created and embedded successfully.")
            return redirect('jobs:job_list')
        except Exception as e:
            messages.error(request, f"Job created but embedding failed: {str(e)}")
            return redirect('jobs:job_list')
            
    return render(request, 'jobs/job_form.html')


def job_detail(request, pk):
    job = get_object_or_404(JobDescription, pk=pk)
    rankings = job.rankings.all().order_by('rank_position')
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'rankings': rankings
    })


def trigger_ranking(request, pk):
    # This is a placeholder as requested
    messages.info(request, "Ranking process triggered (feature coming soon!).")
    return redirect('jobs:job_detail', pk=pk)
