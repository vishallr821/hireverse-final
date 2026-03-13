from django.core.management.base import BaseCommand
from resumes.models import Candidate
from resumes.embedder import embed_resume
from vector_store.chroma_client import add_resume_embedding

class Command(BaseCommand):
    help = 'Regenerates embeddings for all candidates who lack a chroma_id'

    def handle(self, *args, **options):
        candidates = Candidate.objects.filter(chroma_id="")
        processed_count = 0

        for candidate in candidates:
            if not candidate.raw_text:
                self.stdout.write(self.style.WARNING(f"Skipping candidate {candidate.name}: No raw text found."))
                continue

            self.stdout.write(f"Processing candidate: {candidate.name}")
            
            try:
                # Generate embedding
                embedding = embed_resume(candidate.raw_text, candidate.parsed_skills)
                chroma_id = f"candidate_{candidate.id}"
                
                # Add to ChromaDB
                add_resume_embedding(
                    chroma_id=chroma_id,
                    embedding=embedding,
                    metadata={
                        'name': candidate.name,
                        'email': candidate.email or "",
                        'candidate_id': str(candidate.id)
                    }
                )
                
                # Update DB
                candidate.embedding = embedding
                candidate.chroma_id = chroma_id
                candidate.save()
                
                processed_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {candidate.name}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Processed {processed_count} candidates."))
