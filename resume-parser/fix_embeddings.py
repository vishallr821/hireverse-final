import django
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from resumes.models import Candidate
from jobs.models import JobDescription
from resumes.embedder import embed_resume, embed_job_description
from vector_store.chroma_client import add_resume_embedding, add_jd_embedding

def fix_all():
    print("=== Fixing candidate embeddings ===")
    for c in Candidate.objects.all():
        if not c.embedding or len(c.embedding) == 0:
            print(f"Generating embedding for: {c.name}")
            embedding = embed_resume(c.raw_text, c.parsed_skills)
            if embedding:
                c.embedding = embedding
                c.chroma_id = f"candidate_{c.id}"
                c.save()
                try:
                    add_resume_embedding(c.chroma_id, embedding, 
                        {'name': c.name, 'candidate_id': str(c.id)})
                except Exception as e:
                    print(f"ChromaDB error (non-fatal): {e}")
                print(f"  Done! {len(embedding)} dimensions")
            else:
                print(f"  FAILED for {c.name}")
        else:
            print(f"Candidate {c.name} already has embedding ({len(c.embedding)} dims)")

    print("\n=== Fixing job embeddings ===")
    for j in JobDescription.objects.all():
        if not j.embedding or len(j.embedding) == 0:
            print(f"Generating embedding for job: {j.title}")
            embedding = embed_job_description(j.title, j.description, j.required_skills)
            if embedding:
                j.embedding = embedding
                j.chroma_id = f"jd_{j.id}"
                j.save()
                print(f"  Done! {len(embedding)} dimensions")
            else:
                print(f"  FAILED for {j.title}")
        else:
            print(f"Job {j.title} already has embedding ({len(j.embedding)} dims)")

    print("\n=== All done! Now run: python manage.py runserver ===")

if __name__ == "__main__":
    fix_all()
