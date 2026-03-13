import uuid
from django.db import models

class Test(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired')
    ]
    job = models.ForeignKey(
        'jobs.JobDescription',
        on_delete=models.CASCADE,
        related_name='tests'
    )
    candidate = models.ForeignKey(
        'resumes.Candidate',
        on_delete=models.CASCADE,
        related_name='tests'
    )
    ranking_result = models.ForeignKey(
        'ranking.RankingResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tests'
    )
    invite_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    time_limit_minutes = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    aptitude_score = models.FloatField(default=0)
    technical_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)
    ai_report = models.TextField(blank=True)
    head_turn_violations = models.IntegerField(default=0)
    multiple_face_violations = models.IntegerField(default=0)
    tab_switch_violations = models.IntegerField(default=0)
    proctoring_terminated = models.BooleanField(default=False)

    def get_invite_url(self):
        return f"/tests/take/{self.invite_token}/"

    def __str__(self):
        return f"Test: {self.candidate.name} for {self.job.title}"


class Question(models.Model):
    CATEGORY_CHOICES = [
        ('numerical', 'Numerical Aptitude'),
        ('logical', 'Logical Reasoning'),
        ('verbal', 'Verbal Reasoning'),
        ('data', 'Data Interpretation'),
        ('technical', 'Technical MCQ'),
    ]
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    question_text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A','A'),('B','B'),('C','C'),('D','D')]
    )
    explanation = models.TextField(blank=True)
    max_score = models.IntegerField(default=20)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def get_options(self):
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d
        }


class Answer(models.Model):
    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name='answer'
    )
    selected_option = models.CharField(
        max_length=1,
        blank=True
    )
    is_correct = models.BooleanField(null=True)
    score_awarded = models.IntegerField(default=0)
    llm_explanation = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now=True)


class DSASession(models.Model):
    """Links resume-parser test to DSA coding round"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired')
    ]
    
    test = models.OneToOneField(
        Test,
        on_delete=models.CASCADE,
        related_name='dsa_session'
    )
    invite_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # DSA scores from hireverse-dsa
    problems_attempted = models.IntegerField(default=0)
    problems_solved = models.IntegerField(default=0)
    total_dsa_score = models.FloatField(default=0)
    
    # Proctoring
    head_turn_violations = models.IntegerField(default=0)
    multiple_face_violations = models.IntegerField(default=0)
    tab_switch_violations = models.IntegerField(default=0)
    proctoring_terminated = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_invite_url(self):
        return f"/tests/dsa/take/{self.invite_token}/"
    
    def __str__(self):
        return f"DSA Session for {self.test.candidate.name}"


class FinalResult(models.Model):
    """Combined results from both rounds"""
    test = models.OneToOneField(
        Test,
        on_delete=models.CASCADE,
        related_name='final_result'
    )
    dsa_session = models.OneToOneField(
        DSASession,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Test scores
    aptitude_score = models.FloatField(default=0)
    technical_score = models.FloatField(default=0)
    test_total = models.FloatField(default=0)
    
    # DSA scores
    dsa_score = models.FloatField(default=0)
    problems_solved = models.IntegerField(default=0)
    
    # Final
    overall_score = models.FloatField(default=0)
    status = models.CharField(max_length=20, default='pending')
    recommendation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_overall_score(self):
        """Test: 60%, DSA: 40%"""
        self.overall_score = (self.test_total * 0.6) + (self.dsa_score * 0.4)
        self.save()
    
    def __str__(self):
        return f"Final Result: {self.test.candidate.name} - {self.overall_score}%"
