from services.ai.groq_client import call_groq

def generate_feedback(
    problem_statement: str, 
    code: str, 
    language: str,
    passed_cases: int, 
    total_cases: int,
    time_complexity: str, 
    space_complexity: str
) -> str:
    system_prompt = "You are a senior software engineer conducting a technical interview at a top tech company. Be concise, direct, and constructive. Maximum 120 words. No markdown formatting."
    user_prompt = f"""Problem: {problem_statement}
Language: {language}
Student's code:
{code}

Test results: {passed_cases}/{total_cases} cases passed
Time complexity: {time_complexity}
Space complexity: {space_complexity}

Give feedback covering: correctness, efficiency, and one concrete improvement suggestion."""
    
    return call_groq(system_prompt, user_prompt)

def generate_hint(problem_statement: str, code: str, level: int) -> str:
    if level == 1:
        system_prompt = "You are a helpful coding mentor. Give only a subtle nudge."
        user_prompt = f"""Problem: {problem_statement}
Student's current code: {code}
Give a 1-sentence conceptual hint. 
Do NOT mention any algorithm name."""
    elif level == 2:
        system_prompt = "You are a helpful coding mentor."
        user_prompt = f"""Problem: {problem_statement}
Student's current code: {code}
Name the algorithm family they should use and explain why in 2 sentences."""
    elif level == 3:
        system_prompt = "You are a helpful coding mentor."
        user_prompt = f"""Problem: {problem_statement}
Student's current code: {code}
Explain the correct approach clearly. Include pseudocode in at most 6 lines."""
    else:  # level 4
        system_prompt = "You are a helpful coding mentor."
        user_prompt = f"""Problem: {problem_statement}
Language: Python
Show a partial implementation with the key logic filled in but leave the student to complete it."""
        
    return call_groq(system_prompt, user_prompt)

def generate_follow_up(problem_statement: str, code: str) -> str:
    system_prompt = "You are a technical interviewer at a top tech company."
    user_prompt = f"""The candidate just solved this problem correctly:
Problem: {problem_statement}
Their solution: {code}
Ask exactly one sharp follow-up question challenging them to optimise further or handle a new constraint. One sentence only. No preamble."""
    
    return call_groq(system_prompt, user_prompt)

def calculate_dsa_score(passed_cases: int, total_cases: int, time_complexity: str, quality_score: int) -> int:
    if total_cases == 0:
        correctness = 0
    else:
        correctness = (passed_cases / total_cases) * 60
        
    efficiency_bonus = 0
    if time_complexity == "O(1)":
        efficiency_bonus = 20
    elif time_complexity == "O(log n)":
        efficiency_bonus = 20
    elif time_complexity == "O(n)":
        efficiency_bonus = 15
    elif time_complexity == "O(n log n)":
        efficiency_bonus = 10
    elif time_complexity == "O(n²)":
        efficiency_bonus = 5
        
    quality_bonus = min(20, max(0, int(quality_score)))
    
    return int(min(100, correctness + efficiency_bonus + quality_bonus))
