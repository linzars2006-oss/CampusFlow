"""
SmartEdu AI - Database Models
Module: backend/api/models.py

Implements the 10 core schemas + Faculty Interventions:
1. User (Custom AbstractUser with role: admin, faculty, student)
2. Student
3. Faculty
4. Subject
5. Attendance
6. Marks
7. Assignment
8. WeeklySnapshot (Engineered sequential features for LSTM)
9. RiskPrediction
10. Recommendation
11. InterventionNote
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    name = models.CharField(max_length=150)
    roll_no = models.CharField(max_length=50, unique=True)
    class_name = models.CharField(max_length=50, db_column='class')
    section = models.CharField(max_length=10, default='1')
    prev_gpa = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} [{self.roll_no}] - {self.class_name}"


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile', null=True, blank=True)
    name = models.CharField(max_length=150)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prof. {self.name} ({self.department})"


class Subject(models.Model):
    code = models.CharField(max_length=20, default='SUB101')
    name = models.CharField(max_length=150)
    class_name = models.CharField(max_length=50, db_column='class')
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='subjects')

    def __str__(self):
        return f"{self.name} ({self.class_name})"


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances')
    week_number = models.IntegerField(default=1)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    class Meta:
        ordering = ['week_number', 'date']

    def __str__(self):
        return f"Week {self.week_number} - {self.student.name} - {self.status}"


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    checkpoint = models.CharField(max_length=50, help_text='e.g., week_4, internal_1, midterm')
    week_number = models.IntegerField(default=1)
    score = models.FloatField(default=0.0)
    max_score = models.FloatField(default=100.0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} [{self.checkpoint}]: {self.score}/{self.max_score}"


class Assignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    week_number = models.IntegerField(default=1)
    submitted = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)
    max_score = models.FloatField(default=100.0)
    submission_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "Submitted" if self.submitted else "Missing"
        return f"{self.student.name} - W{self.week_number} [{status}]"


class WeeklySnapshot(models.Model):
    """
    Engineered sequence data fed to the LSTM and classical ML models.
    Generated on-demand or weekly per (student, subject, week).
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='snapshots')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='snapshots')
    week_number = models.IntegerField()
    attendance_rate = models.FloatField(default=1.0)
    avg_score_so_far = models.FloatField(default=0.0)
    assignment_submission_rate = models.FloatField(default=1.0)
    marks_trend = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'week_number')
        ordering = ['week_number']

    def __str__(self):
        return f"Snapshot W{self.week_number} - {self.student.name} ({self.subject.name})"


class RiskPrediction(models.Model):
    MODEL_CHOICES = (
        ('rule', 'Rule-Based Baseline'),
        ('ml', 'Classical ML (XGBoost/LogReg)'),
        ('dl', 'Deep Learning (LSTM)'),
    )
    RISK_LEVELS = (
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='risk_predictions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='risk_predictions')
    checkpoint = models.CharField(max_length=50, default='Week 16')
    model_used = models.CharField(max_length=20, choices=MODEL_CHOICES, default='dl')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='low')
    confidence_score = models.FloatField(default=0.85)
    top_factors = models.JSONField(default=list, help_text='SHAP/Attention top contributing factors')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.risk_level.upper()} ({self.model_used})"


class Recommendation(models.Model):
    risk_prediction = models.ForeignKey(RiskPrediction, on_delete=models.CASCADE, related_name='recommendations')
    factor_type = models.CharField(max_length=100)
    recommendation_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rec for {self.risk_prediction.student.name}: {self.factor_type}"


class InterventionNote(models.Model):
    """
    Intervention notes entered by faculty for tracking student support.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='interventions')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='interventions')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note by {self.faculty.name} on {self.student.name} ({self.created_at.strftime('%Y-%m-%d')})"
