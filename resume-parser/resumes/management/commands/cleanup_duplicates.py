import os
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from resumes.models import Candidate

class Command(BaseCommand):
    help = 'Cleans up duplicate candidates based on similar filenames'

    def handle(self, *args, **options):
        self.stdout.write("Starting duplicate cleanup...")
        
        candidates = Candidate.objects.all().order_by('-uploaded_at')
        seen_bases = {}
        deleted_count = 0

        with transaction.atomic():
            for candidate in candidates:
                # Remove Django's random suffix from filename to find the base
                # e.g., resumes/Minojini_-_Resume_enqUtGR.pdf -> Minojini_-_Resume.pdf
                filename = os.path.basename(candidate.resume_file.name)
                # Match pattern like _[8 random chars] before extension
                base_name = re.sub(r'_[a-zA-Z0-9]{7}\.', '.', filename)
                
                # Also normalize by name if email is empty
                identity_key = f"{base_name.lower()}_{candidate.name.lower()}"
                
                if identity_key in seen_bases:
                    # Keep the one we saw first (oldest) or last (newest)? 
                    # Usually newest is better if parsing improved.
                    # Let's keep the one already in the dict and delete this one.
                    # Or update the dict to keep this one and delete the old one.
                    # To follow common practices, let's keep the latest one.
                    old_candidate = seen_bases[identity_key]
                    self.stdout.write(f"Deleting duplicate: {candidate.name} (ID: {candidate.id}, File: {filename})")
                    
                    # Delete the file from storage
                    if candidate.resume_file:
                        if os.path.exists(candidate.resume_file.path):
                            os.remove(candidate.resume_file.path)
                    
                    candidate.delete()
                    deleted_count += 1
                else:
                    seen_bases[identity_key] = candidate

        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} duplicate candidates."))
