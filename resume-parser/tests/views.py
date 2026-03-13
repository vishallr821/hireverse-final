from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
import datetime
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from .models import Test, Question, Answer, DSASession, FinalResult
from .question_generator import generate_aptitude_questions
from .evaluator import evaluate_full_test
from .proctoring import ProctorMonitor


def generate_test(request, candidate_id, job_id):
    from resumes.models import Candidate
    from jobs.models import JobDescription

    candidate = get_object_or_404(Candidate, id=candidate_id)
    job = get_object_or_404(JobDescription, id=job_id)

    existing = Test.objects.filter(
        candidate=candidate,
        job=job
    ).order_by('-created_at').first()

    if existing:
        invite_url = request.build_absolute_uri(
            existing.get_invite_url()
        )
        return render(request, 'tests/invite_ready.html', {
            'test': existing,
            'invite_url': invite_url,
            'candidate': candidate,
            'job': job,
            'already_exists': True,
            'test_status': existing.status
        })

    print(f"Generating questions for {candidate.name}...")
    questions_data = generate_aptitude_questions(
        job.title,
        job.required_skills,
        job.description
    )

    test = Test.objects.create(
        job=job,
        candidate=candidate,
        time_limit_minutes=30
    )

    for q in questions_data.get('questions', []):
        Question.objects.create(
            test=test,
            category=q.get('category', 'numerical'),
            question_text=q.get('question_text', ''),
            option_a=q.get('option_a', ''),
            option_b=q.get('option_b', ''),
            option_c=q.get('option_c', ''),
            option_d=q.get('option_d', ''),
            correct_option=q.get('correct_option', 'A'),
            explanation=q.get('explanation', ''),
            max_score=q.get('max_score', 20),
            order=q.get('order', 1)
        )

    invite_url = request.build_absolute_uri(
        test.get_invite_url()
    )
    print(f"Test created! URL: {invite_url}")

    return render(request, 'tests/invite_ready.html', {
        'test': test,
        'invite_url': invite_url,
        'candidate': candidate,
        'job': job,
        'already_exists': False
    })


def send_test_link(request, candidate_id, job_id, ranking_id):
    from resumes.models import Candidate
    from jobs.models import JobDescription
    from ranking.models import RankingResult

    candidate = get_object_or_404(Candidate, id=candidate_id)
    job = get_object_or_404(JobDescription, id=job_id)
    ranking = get_object_or_404(RankingResult, id=ranking_id)

    # Check if a test already exists for this ranking session
    test = Test.objects.filter(
        candidate=candidate,
        job=job,
        ranking_result=ranking
    ).first()

    if not test:
        # If no test for this ranking, try to find a pending test for this cand/job
        test = Test.objects.filter(
            candidate=candidate,
            job=job,
            status='pending'
        ).first()
        
        if not test:
            # Generate new questions if needed (reusing logic from generate_test would be better, but keeping it simple)
            questions_data = generate_aptitude_questions(
                job.title,
                job.required_skills,
                job.description
            )
            test = Test.objects.create(
                job=job,
                candidate=candidate,
                ranking_result=ranking,
                time_limit_minutes=30
            )
            for q in questions_data.get('questions', []):
                Question.objects.create(
                    test=test,
                    category=q.get('category', 'numerical'),
                    question_text=q.get('question_text', ''),
                    option_a=q.get('option_a', ''),
                    option_b=q.get('option_b', ''),
                    option_c=q.get('option_c', ''),
                    option_d=q.get('option_d', ''),
                    correct_option=q.get('correct_option', 'A'),
                    explanation=q.get('explanation', ''),
                    max_score=q.get('max_score', 20),
                    order=q.get('order', 1)
                )

    # Update status to 'sent' and record timestamp
    test.ranking_result = ranking
    test.status = 'sent'
    test.sent_at = timezone.now()
    test.save()

    # In a real app, send actual email here.
    print(f"EMAIL SENT: Assessment link sent to {candidate.email}")

    return redirect('ranking:ranking_results', pk=job_id)


def take_test(request, token):
    test = get_object_or_404(Test, invite_token=token)

    # Step 4 Expiration Check: 48 hours
    if test.status == 'sent' and test.sent_at:
        if timezone.now() > test.sent_at + datetime.timedelta(hours=48):
            test.status = 'expired'
            test.save()

    if test.status == 'completed':
        return redirect('tests:test_result', token=token)

    if test.status == 'expired':
        return render(request, 'tests/test_expired.html', {
            'test': test
        })

    if test.status == 'active' and test.started_at:
        elapsed = timezone.now() - test.started_at
        limit = datetime.timedelta(
            minutes=test.time_limit_minutes
        )
        if elapsed > limit:
            test.status = 'expired'
            test.save()
            return render(request, 'tests/test_expired.html', {'test': test})

    if test.status in ['pending', 'sent']:
        test.status = 'active'
        test.started_at = timezone.now()
        test.save()

    questions = test.questions.all().order_by('order')

    return render(request, 'tests/test_interface.html', {
        'test': test,
        'questions': questions,
        'time_limit_seconds': test.time_limit_minutes * 60
    })


@require_POST
def submit_test(request, token):
    test = get_object_or_404(Test, invite_token=token)

    if test.status == 'completed':
        return redirect('tests:test_result', token=token)

    questions = test.questions.all()
    for question in questions:
        Answer.objects.filter(question=question).delete()
        selected = request.POST.get(f'question_{question.id}', '')
        Answer.objects.create(
            question=question,
            selected_option=selected.upper() if selected else ''
        )

    print(f"Evaluating test for {test.candidate.name}...")
    evaluate_full_test(test.id)

    return redirect('tests:test_result', token=token)


def test_result(request, token):
    test = get_object_or_404(Test, invite_token=token)
    questions = test.questions.all().order_by('order')

    results_data = []
    for q in questions:
        try:
            ans = q.answer
        except Answer.DoesNotExist:
            ans = None
        results_data.append({
            'question': q,
            'answer': ans,
            'options': q.get_options()
        })

    return render(request, 'tests/test_result.html', {
        'test': test,
        'results_data': results_data
    })


def test_list(request):
    tests = Test.objects.all().order_by('-created_at')
    return render(request, 'tests/test_list.html', {
        'tests': tests
    })


@csrf_exempt
@require_POST
def check_proctoring(request, token):
    """API endpoint to check proctoring violations"""
    try:
        test = get_object_or_404(Test, invite_token=token)
        
        if test.status != 'active':
            return JsonResponse({'error': 'Test not active'}, status=400)
        
        data = json.loads(request.body)
        frame_data = data.get('frame')
        
        if not frame_data:
            return JsonResponse({'error': 'No frame data'}, status=400)
        
        # Decode base64 frame
        import base64
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        
        monitor = ProctorMonitor()
        violations = monitor.analyze_frame(frame_bytes)
        monitor.cleanup()
        
        # Track violations
        terminate = False
        warning = None
        
        if violations['head_turned']:
            test.head_turn_violations += 1
            if test.head_turn_violations >= 5:
                test.proctoring_terminated = True
                test.status = 'completed'
                terminate = True
            else:
                warning = f"Head turn detected ({test.head_turn_violations}/5)"
        
        if violations['face_count'] > 1:
            test.multiple_face_violations += 1
            if test.multiple_face_violations == 1:
                warning = "Multiple faces detected! Warning 1/5"
            elif test.multiple_face_violations >= 5:
                test.proctoring_terminated = True
                test.status = 'completed'
                terminate = True
            else:
                warning = f"Multiple faces detected ({test.multiple_face_violations}/5)"
        
        test.save()
        
        return JsonResponse({
            'violations': violations,
            'head_turn_count': test.head_turn_violations,
            'multiple_face_count': test.multiple_face_violations,
            'terminate': terminate,
            'warning': warning
        })
        
    except Exception as e:
        import traceback
        print(f"Proctoring error: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


def send_to_dsa_round(request, test_id):
    """Send qualified candidate to DSA coding round"""
    test = get_object_or_404(Test, id=test_id)
    
    # Check if test is completed and candidate qualified (e.g., score >= 50%)
    if test.status != 'completed':
        return JsonResponse({'error': 'Test not completed'}, status=400)
    
    if test.total_score < 50:
        return JsonResponse({'error': 'Candidate did not qualify'}, status=400)
    
    # Create or get DSA session
    dsa_session, created = DSASession.objects.get_or_create(
        test=test,
        defaults={'status': 'sent', 'sent_at': timezone.now()}
    )
    
    if not created:
        dsa_session.status = 'sent'
        dsa_session.sent_at = timezone.now()
        dsa_session.save()
    
    # Create final result entry
    final_result, _ = FinalResult.objects.get_or_create(
        test=test,
        defaults={
            'dsa_session': dsa_session,
            'aptitude_score': test.aptitude_score,
            'technical_score': test.technical_score,
            'test_total': test.total_score
        }
    )
    
    invite_url = request.build_absolute_uri(dsa_session.get_invite_url())
    
    print(f"DSA Round link sent to {test.candidate.email}: {invite_url}")
    
    return render(request, 'tests/dsa_invite_ready.html', {
        'test': test,
        'dsa_session': dsa_session,
        'invite_url': invite_url
    })


def dsa_take(request, token):
    """Redirect to DSA platform with candidate info"""
    dsa_session = get_object_or_404(DSASession, invite_token=token)
    
    # Check expiration
    if dsa_session.status == 'sent' and dsa_session.sent_at:
        if timezone.now() > dsa_session.sent_at + datetime.timedelta(hours=48):
            dsa_session.status = 'expired'
            dsa_session.save()
    
    if dsa_session.status == 'expired':
        return render(request, 'tests/dsa_expired.html', {'dsa_session': dsa_session})
    
    if dsa_session.status == 'completed':
        return redirect('tests:final_results', test_id=dsa_session.test.id)
    
    # Mark as active
    if dsa_session.status in ['pending', 'sent']:
        dsa_session.status = 'active'
        dsa_session.started_at = timezone.now()
        dsa_session.save()
    
    # Render DSA interface with proctoring
    return render(request, 'tests/dsa_interface.html', {
        'dsa_session': dsa_session,
        'test': dsa_session.test,
        'candidate': dsa_session.test.candidate
    })


@csrf_exempt
@require_POST
def check_dsa_proctoring(request, token):
    """Proctoring for DSA round"""
    try:
        dsa_session = get_object_or_404(DSASession, invite_token=token)
        
        if dsa_session.status != 'active':
            return JsonResponse({'error': 'DSA session not active'}, status=400)
        
        data = json.loads(request.body)
        frame_data = data.get('frame')
        
        if not frame_data:
            return JsonResponse({'error': 'No frame data'}, status=400)
        
        import base64
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        
        monitor = ProctorMonitor()
        violations = monitor.analyze_frame(frame_bytes)
        monitor.cleanup()
        
        terminate = False
        warning = None
        
        if violations['head_turned']:
            dsa_session.head_turn_violations += 1
            if dsa_session.head_turn_violations >= 5:
                dsa_session.proctoring_terminated = True
                dsa_session.status = 'completed'
                terminate = True
            else:
                warning = f"Head turn detected ({dsa_session.head_turn_violations}/5)"
        
        if violations['face_count'] > 1:
            dsa_session.multiple_face_violations += 1
            if dsa_session.multiple_face_violations == 1:
                warning = "Multiple faces detected! Warning 1/5"
            elif dsa_session.multiple_face_violations >= 5:
                dsa_session.proctoring_terminated = True
                dsa_session.status = 'completed'
                terminate = True
            else:
                warning = f"Multiple faces detected ({dsa_session.multiple_face_violations}/5)"
        
        dsa_session.save()
        
        return JsonResponse({
            'violations': violations,
            'head_turn_count': dsa_session.head_turn_violations,
            'multiple_face_count': dsa_session.multiple_face_violations,
            'terminate': terminate,
            'warning': warning
        })
        
    except Exception as e:
        import traceback
        print(f"DSA Proctoring error: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


def final_results(request, test_id):
    """Show combined results from both rounds"""
    test = get_object_or_404(Test, id=test_id)
    
    try:
        final_result = test.final_result
        dsa_session = test.dsa_session
    except:
        final_result = None
        dsa_session = None
    
    return render(request, 'tests/final_results.html', {
        'test': test,
        'dsa_session': dsa_session,
        'final_result': final_result
    })


def all_final_results(request):
    """List all candidates with combined scores"""
    final_results = FinalResult.objects.select_related(
        'test__candidate', 'test__job', 'dsa_session'
    ).order_by('-overall_score')
    
    return render(request, 'tests/all_final_results.html', {
        'final_results': final_results
    })
