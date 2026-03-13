from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = 'BAAI/bge-base-en-v1.5'
_model = None

def get_model():
    """Lazy loads and returns the SentenceTransformer model with robust error handling"""
    global _model
    if _model is None:
        try:
            print(f"Loading {MODEL_NAME} model... (this may take a moment)")
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(MODEL_NAME)
            print("Model loaded successfully!")
        except Exception as e:
            print(f"EMBEDDING MODEL FAILED TO LOAD: {e}")
            return None
    return _model

def embed_text(text: str) -> list:
    """Generates an embedding for the given text with error handling"""
    model = get_model()
    if model is None:
        print("WARNING: No embedding model available, returning empty list")
        return []
    try:
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        print(f"EMBEDDING FAILED: {e}")
        return []

def embed_resume(candidate_raw_text: str, candidate_skills: list) -> list:
    """Creates a combined embedding for a resume"""
    skills_text = ", ".join(candidate_skills)
    combined_text = f"{skills_text} {candidate_raw_text[:1000]}"
    return embed_text(combined_text)

def embed_job_description(jd_title: str, jd_description: str, jd_required_skills: str) -> list:
    """Creates a combined embedding for a job description"""
    combined_text = f"{jd_title}. {jd_required_skills}. {jd_description[:800]}"
    return embed_text(combined_text)
