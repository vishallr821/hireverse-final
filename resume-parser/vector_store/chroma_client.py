import chromadb
from chromadb.config import Settings
import os

CHROMA_PATH = 'vector_store/chroma_data'

def get_client():
    """Returns a persistent ChromaDB client"""
    if not os.path.exists(CHROMA_PATH):
        os.makedirs(CHROMA_PATH)
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_resume_collection():
    """Returns the 'resumes' collection, creates if it doesn't exist"""
    client = get_client()
    return client.get_or_create_collection(name="resumes")

def get_jd_collection():
    """Returns the 'job_descriptions' collection, creates if it doesn't exist"""
    client = get_client()
    return client.get_or_create_collection(name="job_descriptions")

def add_resume_embedding(chroma_id: str, embedding: list, metadata: dict):
    """Adds a resume embedding to the 'resumes' collection"""
    collection = get_resume_collection()
    collection.add(
        ids=[chroma_id],
        embeddings=[embedding],
        metadatas=[metadata]
    )

def add_jd_embedding(chroma_id: str, embedding: list, metadata: dict):
    """Adds a job description embedding to the 'job_descriptions' collection"""
    collection = get_jd_collection()
    collection.add(
        ids=[chroma_id],
        embeddings=[embedding],
        metadatas=[metadata]
    )

def query_resumes(jd_embedding: list, n_results: int = 10) -> dict:
    """Queries the 'resumes' collection with a JD embedding"""
    collection = get_resume_collection()
    results = collection.query(
        query_embeddings=[jd_embedding],
        n_results=n_results
    )
    return results

def delete_resume(chroma_id: str):
    """Deletes a resume from the 'resumes' collection by ID"""
    collection = get_resume_collection()
    collection.delete(ids=[chroma_id])

def get_all_resume_ids() -> list:
    """Returns all IDs currently in the 'resumes' collection"""
    collection = get_resume_collection()
    results = collection.get()
    return results.get('ids', [])
