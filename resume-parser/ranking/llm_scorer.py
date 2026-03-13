import os
import json
import re
from dotenv import load_dotenv
load_dotenv()

def extract_json_from_response(text: str) -> dict:
    default = {
        "score": 0,
        "seniority_level": "Unknown",
        "strengths": [],
        "skill_gaps": [],
        "recommendation": "No",
        "reasoning": "Could not analyze candidate."
    }
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return default

def score_candidate(job_title: str, job_description: str,
                    required_skills: str, resume_text: str,
                    candidate_skills: list) -> dict:
    try:
        from groq import Groq
        
        api_key = os.environ.get('GROQ_API_KEY', '')
        if not api_key:
            print("WARNING: GROQ_API_KEY not found!")
            return extract_json_from_response("")
            
        client = Groq(api_key=api_key)
        
        prompt = f"""You are an expert technical recruiter.
Analyze this candidate against the job and return ONLY 
a valid JSON object.

Job Title: {job_title}
Required Skills: {required_skills}
Job Description: {job_description[:400]}

Candidate Skills: {', '.join(candidate_skills)}
Resume Summary: {resume_text[:800]}

Return ONLY this exact JSON structure, nothing else:
{{
  "score": <integer 0-100>,
  "seniority_level": "<Junior or Mid or Senior or Lead>",
  "strengths": ["strength1", "strength2", "strength3"],
  "skill_gaps": ["gap1", "gap2"],
  "recommendation": "<Strong Yes or Yes or Maybe or No>",
  "reasoning": "<2 sentences explaining the score>"
}}"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical recruiter. Always respond with valid JSON only. No markdown, no explanation, just JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=400,
            temperature=0.1
        )
        
        output = response.choices[0].message.content
        print(f"Groq response: {output[:200]}")
        return extract_json_from_response(output)
        
    except Exception as e:
        print(f"Groq API error: {e}")
        return {
            "score": 0,
            "seniority_level": "Unknown",
            "strengths": [],
            "skill_gaps": [],
            "recommendation": "No",
            "reasoning": f"API error: {str(e)}"
        }
