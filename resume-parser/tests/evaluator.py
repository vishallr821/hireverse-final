import os
import json
import re
from dotenv import load_dotenv
load_dotenv()

CATEGORY_LABELS = {
    'numerical': 'Numerical Aptitude',
    'logical': 'Logical Reasoning',
    'verbal': 'Verbal Reasoning',
    'data': 'Data Interpretation',
    'technical': 'Technical MCQ'
}

def evaluate_single_answer(
        question_text: str,
        options: dict,
        correct_option: str,
        selected_option: str,
        explanation: str,
        max_score: int) -> dict:

    is_correct = (selected_option.upper() == correct_option.upper())
    score = max_score if is_correct else 0

    try:
        from groq import Groq
        client = Groq(api_key=os.environ.get('GROQ_API_KEY',''))

        correct_text = options.get(correct_option, '')
        selected_text = options.get(selected_option, 'Not answered') if selected_option else 'Not answered'

        prompt = f"""A candidate answered an aptitude question.
Give a brief educational explanation.

Question: {question_text}
Correct Answer: {correct_option}) {correct_text}
Candidate Selected: {selected_option}) {selected_text}
Result: {'CORRECT' if is_correct else 'INCORRECT'}
Official Explanation: {explanation}

Write exactly 2 sentences:
1. Why the correct answer is right
2. A helpful tip to remember this type of question

Keep it encouraging and educational."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful tutor explaining aptitude answers. Be concise and encouraging."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=150,
            temperature=0.3
        )

        llm_explanation = response.choices[0].message.content.strip()

    except Exception as e:
        print(f"LLM explanation error: {e}")
        llm_explanation = explanation

    return {
        'is_correct': is_correct,
        'score': score,
        'llm_explanation': llm_explanation
    }


def evaluate_full_test(test_id: int) -> dict:
    from tests.models import Test, Answer
    from ranking.models import RankingResult
    from django.utils import timezone

    test = Test.objects.get(id=test_id)
    questions = test.questions.all().order_by('order')

    total_score = 0
    max_total = 0
    aptitude_score = 0
    technical_score = 0
    max_aptitude = 0
    max_technical = 0
    report_lines = []

    for question in questions:
        max_total += question.max_score
        
        try:
            answer = question.answer
            selected = answer.selected_option or ''
        except Answer.DoesNotExist:
            continue

        result = evaluate_single_answer(
            question_text=question.question_text,
            options=question.get_options(),
            correct_option=question.correct_option,
            selected_option=selected,
            explanation=question.explanation,
            max_score=question.max_score
        )

        answer.is_correct = result['is_correct']
        answer.score_awarded = result['score']
        answer.llm_explanation = result['llm_explanation']
        answer.save()

        total_score += result['score']

        label = CATEGORY_LABELS.get(question.category, question.category)
        status = '✓ Correct' if result['is_correct'] else '✗ Incorrect'
        report_lines.append(f"Q{question.order} {label}: {status} ({result['score']}/{question.max_score})")

        if question.category == 'technical':
            technical_score += result['score']
            max_technical += question.max_score
        else:
            aptitude_score += result['score']
            max_aptitude += question.max_score

    apt_pct = round((aptitude_score/max_aptitude*100), 1) if max_aptitude > 0 else 0
    tech_pct = round((technical_score/max_technical*100), 1) if max_technical > 0 else 0
    total_pct = round((total_score/max_total*100), 1) if max_total > 0 else 0

    test.aptitude_score = apt_pct
    test.technical_score = tech_pct
    test.total_score = total_pct
    test.status = 'completed'
    test.completed_at = timezone.now()
    test.ai_report = '\n'.join(report_lines)
    test.save()

    print(f"Test evaluated: {total_pct}% total")

    try:
        ranking = RankingResult.objects.filter(
            job=test.job,
            candidate=test.candidate
        ).first()
        if ranking:
            old_score = ranking.final_score
            new_score = round((old_score * 0.7) + (total_pct * 0.3), 2)
            ranking.final_score = new_score
            ranking.save()
            print(f"Ranking updated: {old_score} → {new_score}")
    except Exception as e:
        print(f"Ranking update error (non-fatal): {e}")

    return {
        'aptitude_score': apt_pct,
        'technical_score': tech_pct,
        'total_score': total_pct
    }
