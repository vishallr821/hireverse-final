import numpy as np

def cosine_similarity(vec1: list, vec2: list) -> float:
    """Computes cosine similarity between two vectors."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    score = np.dot(v1, v2) / (norm_v1 * norm_v2)
    return float(round(score, 4))

def rank_all_candidates(jd_embedding: list, candidates: list) -> list:
    """Ranks candidates by cosine similarity to JD embedding."""
    results = []
    for candidate in candidates:
        score = cosine_similarity(jd_embedding, candidate['embedding'])
        results.append({
            'candidate_id': candidate['candidate_id'],
            'name': candidate['name'],
            'cosine_score': score
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x['cosine_score'], reverse=True)
    return results

def get_top_n(ranked_list: list, n: int = 10) -> list:
    """Returns top n results."""
    return ranked_list[:n]

def compute_similarity_matrix(jd_embeddings: list, resume_embeddings: list) -> list:
    """Computes similarity matrix between all JDs and resumes."""
    matrix = []
    for jd_emb in jd_embeddings:
        row = []
        for resume_emb in resume_embeddings:
            row.append(cosine_similarity(jd_emb, resume_emb))
        matrix.append(row)
    return matrix
