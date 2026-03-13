# HireVerse Integration Guide
## Resume Parser + DSA Coding Platform

This guide explains how to integrate the resume-parser (Django) with hireverse-dsa (FastAPI) projects.

## Architecture Overview

```
Candidate Flow:
1. Resume Upload → Ranking
2. Aptitude/Technical Test (Proctored) → Score
3. If Score >= 50% → DSA Coding Round (Proctored)
4. Final Results (Combined Score)
```

## Setup Instructions

### 1. Database Migrations

```bash
cd d:\Final\resume-parser
python manage.py makemigrations
python manage.py migrate
```

### 2. Start Both Servers

**Terminal 1 - Django (Resume Parser):**
```bash
cd d:\Final\resume-parser
python manage.py runserver 8000
```

**Terminal 2 - FastAPI (DSA Platform):**
```bash
cd d:\Final\hireverse-dsa
uvicorn main:app --reload --port 8001
```

## Integration Points

### 1. Sending Candidates to DSA Round

After a test is completed, if the candidate scores >= 50%:

**URL:** `/tests/send-dsa/<test_id>/`

**Button Location:** Test Result Page

**What it does:**
- Creates DSASession record
- Generates unique invite token
- Links to Test record
- Creates FinalResult entry

### 2. DSA Interface with Proctoring

**URL:** `/dsa/take/<token>/`

**Features:**
- Embeds DSA platform in iframe
- Webcam proctoring active
- Tracks violations
- Auto-terminates on 3 violations

### 3. Proctoring Endpoints

**Test Proctoring:** `/tests/proctor/<token>/`
**DSA Proctoring:** `/tests/dsa/proctor/<token>/`

Both use OpenCV Haar Cascades for:
- Face detection (multiple faces)
- Profile detection (head turned)

### 4. Final Results

**Individual:** `/tests/final-results/<test_id>/`
**All Candidates:** `/tests/all-final-results/`

Shows:
- Test scores (Aptitude + Technical)
- DSA scores
- Overall score (Test 60% + DSA 40%)
- Recommendation

## Database Models

### DSASession
```python
- test (OneToOne → Test)
- invite_token (UUID)
- status (pending/sent/active/completed/expired)
- problems_attempted, problems_solved
- total_dsa_score
- proctoring violations
```

### FinalResult
```python
- test (OneToOne → Test)
- dsa_session (OneToOne → DSASession)
- aptitude_score, technical_score, test_total
- dsa_score, problems_solved
- overall_score (calculated)
- recommendation
```

## Scoring System

### Test Round (100%)
- Aptitude: 50%
- Technical: 50%

### DSA Round (100%)
- Based on problems solved
- Code quality
- Time/Space complexity

### Overall Score
- Test: 60% weight
- DSA: 40% weight

### Recommendations
- >= 70%: Recommended for Hire
- 50-69%: Consider for Interview
- < 50%: Not Recommended

## Proctoring System

### Violations Tracked
1. **Head Turn:** Profile face detected
2. **Multiple Faces:** More than 1 face in frame

### Thresholds
- 5 violations → Auto-terminate
- Warnings shown at 1, 2, 3, and 4 violations

### Configuration
Edit `tests/proctoring.py`:
```python
# Adjust detection sensitivity
scaleFactor=1.1  # Lower = more strict
minNeighbors=5   # Higher = more strict
```

## API Communication

### DSA Platform Integration

The DSA interface is embedded via iframe:
```html
<iframe src="http://localhost:8001/problems?candidate_id={{ dsa_session.id }}">
```

### Updating DSA Scores

When DSA round completes, update via:
```python
dsa_session.problems_attempted = X
dsa_session.problems_solved = Y
dsa_session.total_dsa_score = Z
dsa_session.status = 'completed'
dsa_session.save()

# Update final result
final_result.dsa_score = Z
final_result.problems_solved = Y
final_result.calculate_overall_score()
```

## Workflow Example

### Step 1: Complete Test
```
Candidate completes test → Score: 65%
Button appears: "Send to DSA Round"
```

### Step 2: Send to DSA
```
Click button → DSASession created
Invite link generated: /dsa/take/<token>/
Email sent to candidate (simulated)
```

### Step 3: Take DSA Round
```
Candidate clicks link → DSA interface loads
Webcam starts → Proctoring active
Solves problems → Scores recorded
```

### Step 4: View Results
```
Navigate to: /tests/final-results/<test_id>/
Shows:
- Test: 65%
- DSA: 75%
- Overall: 68% (65*0.6 + 75*0.4)
- Recommendation: Consider for Interview
```

## Troubleshooting

### Issue: Proctoring not working
**Solution:** Ensure OpenCV is installed:
```bash
pip install opencv-python
```

### Issue: DSA iframe not loading
**Solution:** Check DSA server is running on port 8001

### Issue: Migrations fail
**Solution:** Delete db.sqlite3 and run:
```bash
python manage.py migrate
```

### Issue: Camera access denied
**Solution:** Use HTTPS or localhost (required by browsers)

## Production Deployment

### Security Considerations
1. Use HTTPS for both servers
2. Add CORS configuration
3. Implement proper authentication
4. Store videos/screenshots if needed
5. Add rate limiting to proctoring endpoints

### Environment Variables
```env
# .env for resume-parser
DSA_PLATFORM_URL=https://dsa.yourcompany.com

# .env for hireverse-dsa
RESUME_PARSER_URL=https://hiring.yourcompany.com
```

### Reverse Proxy (Nginx)
```nginx
location /dsa/ {
    proxy_pass http://localhost:8001/;
}

location / {
    proxy_pass http://localhost:8000/;
}
```

## Testing the Integration

### 1. Create Test Data
```bash
# In Django shell
python manage.py shell

from tests.models import Test
from resumes.models import Candidate
from jobs.models import JobDescription

# Create test with high score
test = Test.objects.first()
test.total_score = 75
test.status = 'completed'
test.save()
```

### 2. Test Flow
1. Go to test results
2. Click "Send to DSA Round"
3. Copy invite link
4. Open in new tab
5. Allow camera access
6. Verify proctoring works
7. Complete DSA problems
8. View final results

## Support

For issues or questions:
- Check logs in terminal
- Review browser console for JS errors
- Verify both servers are running
- Check database migrations applied

## Future Enhancements

- [ ] Email notifications
- [ ] SMS alerts for violations
- [ ] Video recording
- [ ] Eye tracking
- [ ] Tab switching detection
- [ ] Audio monitoring
- [ ] AI-based behavior analysis
- [ ] Automated scheduling
- [ ] Candidate dashboard
- [ ] Analytics and reports
