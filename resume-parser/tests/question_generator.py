import os
import json
import re
from dotenv import load_dotenv
load_dotenv()

def parse_questions(raw_text: str) -> dict:
    try:
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"JSON parse error: {e}")
    return {}

def generate_aptitude_questions(
        job_title: str,
        required_skills: str,
        job_description: str) -> dict:
    try:
        from groq import Groq
        client = Groq(api_key=os.environ.get('GROQ_API_KEY',''))

        prompt = f"""You are creating an aptitude test for 
a job candidate. Generate exactly 5 MCQ questions.

Job Title: {job_title}
Required Skills: {required_skills}

Rules:
- Q1: Numerical Aptitude (speed/time/profit/percentage)
- Q2: Logical Reasoning (series/pattern/analogy)
- Q3: Verbal Reasoning (vocabulary/sentence completion)
- Q4: Data Interpretation (simple table or calculation)
- Q5: Technical MCQ specific to: {job_title} 
  and skills: {required_skills}

Each question must have exactly 4 options (A,B,C,D) 
and one correct answer.

Return ONLY this exact JSON, nothing else:
{{
  "questions": [
    {{
      "order": 1,
      "category": "numerical",
      "question_text": "A train covers 360km in 4 hours. What is its speed in m/s?",
      "option_a": "25 m/s",
      "option_b": "30 m/s",
      "option_c": "20 m/s",
      "option_d": "35 m/s",
      "correct_option": "A",
      "explanation": "Speed = 360/4 = 90 km/h = 90 x 5/18 = 25 m/s",
      "max_score": 20
    }},
    {{
      "order": 2,
      "category": "logical",
      "question_text": "2, 6, 12, 20, 30, ?",
      "option_a": "40",
      "option_b": "42",
      "option_c": "44",
      "option_d": "38",
      "correct_option": "B",
      "explanation": "Pattern: differences are 4,6,8,10,12. Next = 30+12 = 42",
      "max_score": 20
    }},
    {{
      "order": 3,
      "category": "verbal",
      "question_text": "Choose the word most similar to ELOQUENT:",
      "option_a": "Silent",
      "option_b": "Articulate",
      "option_c": "Confused",
      "option_d": "Hesitant",
      "correct_option": "B",
      "explanation": "Eloquent means fluent and persuasive in speaking, similar to articulate",
      "max_score": 20
    }},
    {{
      "order": 4,
      "category": "data",
      "question_text": "A team completed 40% of a project in 20 days. At this rate, how many more days to finish the remaining 60%?",
      "option_a": "25 days",
      "option_b": "30 days",
      "option_c": "35 days",
      "option_d": "40 days",
      "correct_option": "B",
      "explanation": "40% in 20 days, so 60% takes 20 x (60/40) = 30 days",
      "max_score": 20
    }},
    {{
      "order": 5,
      "category": "technical",
      "question_text": "A technical question specific to {job_title}",
      "option_a": "Option A",
      "option_b": "Option B",
      "option_c": "Option C",
      "option_d": "Option D",
      "correct_option": "A",
      "explanation": "Explanation of why this is correct",
      "max_score": 20
    }}
  ]
}}"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an aptitude test creator. Return valid JSON only. No markdown, no explanation, just the JSON object."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.4
        )

        raw = response.choices[0].message.content
        print(f"Generator response preview: {raw[:400]}")
        result = parse_questions(raw)

        if not result or 'questions' not in result:
            print("LLM returned invalid JSON, using fallback")
            return get_fallback_questions(job_title, required_skills)

        if len(result['questions']) != 5:
            print(f"Expected 5 questions, got {len(result['questions'])}, using fallback")
            return get_fallback_questions(job_title, required_skills)

        return result

    except Exception as e:
        print(f"Question generation error: {e}")
        return get_fallback_questions(job_title, required_skills)


def get_fallback_questions(job_title: str, required_skills: str) -> dict:
    return {
        "questions": [
            {
                "order": 1,
                "category": "numerical",
                "question_text": "A man buys an article for Rs.800 and sells it for Rs.1000. What is the profit percentage?",
                "option_a": "20%",
                "option_b": "25%",
                "option_c": "15%",
                "option_d": "30%",
                "correct_option": "B",
                "explanation": "Profit = 200, Profit% = (200/800) x 100 = 25%",
                "max_score": 20
            },
            {
                "order": 2,
                "category": "logical",
                "question_text": "If all roses are flowers and some flowers fade quickly, which conclusion is valid?",
                "option_a": "All roses fade quickly",
                "option_b": "Some roses may fade quickly",
                "option_c": "No roses fade quickly",
                "option_d": "All flowers are roses",
                "correct_option": "B",
                "explanation": "Since only some flowers fade quickly, some roses (being flowers) may also fade quickly",
                "max_score": 20
            },
            {
                "order": 3,
                "category": "verbal",
                "question_text": "Choose the odd one out: Python, Java, HTML, C++",
                "option_a": "Python",
                "option_b": "Java",
                "option_c": "HTML",
                "option_d": "C++",
                "correct_option": "C",
                "explanation": "HTML is a markup language, not a programming language like the others",
                "max_score": 20
            },
            {
                "order": 4,
                "category": "data",
                "question_text": "If a project needs 6 developers to complete in 10 days, how many developers are needed to complete it in 4 days?",
                "option_a": "12",
                "option_b": "15",
                "option_c": "18",
                "option_d": "20",
                "correct_option": "B",
                "explanation": "Total work = 6 x 10 = 60 dev-days. Developers needed = 60/4 = 15",
                "max_score": 20
            },
            {
                "order": 5,
                "category": "technical",
                "question_text": f"Which of these is a key concept in {job_title} roles?",
                "option_a": "Version control with Git",
                "option_b": "Manual paper filing",
                "option_c": "Typewriter usage",
                "option_d": "Fax machine operation",
                "correct_option": "A",
                "explanation": f"Version control is fundamental in any {job_title} technical role",
                "max_score": 20
            }
        ]
    }
