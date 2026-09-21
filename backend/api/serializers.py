"""
SmartEdu AI - API Serializers
Module: backend/api/serializers.py
"""

from rest_framework import serializers
from api.models import (
    User, Student, Faculty, Subject,
    Attendance, Marks, Assignment,
    WeeklySnapshot, RiskPrediction, Recommendation,
    InterventionNote
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'student'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class StudentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'name', 'roll_no', 'class_name', 'section', 'prev_gpa', 'email', 'username', 'created_at']


class FacultySerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Faculty
        fields = ['id', 'name', 'department', 'email', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'class_name', 'faculty', 'faculty_name']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    roll_no = serializers.CharField(source='student.roll_no', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'roll_no', 'subject', 'week_number', 'date', 'status']


class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    roll_no = serializers.CharField(source='student.roll_no', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Marks
        fields = ['id', 'student', 'student_name', 'roll_no', 'subject', 'subject_name', 'checkpoint', 'week_number', 'score', 'max_score', 'date']


class AssignmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    roll_no = serializers.CharField(source='student.roll_no', read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'student', 'student_name', 'roll_no', 'subject', 'week_number', 'submitted', 'score', 'max_score', 'submission_date']


class WeeklySnapshotSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)

    class Meta:
        model = WeeklySnapshot
        fields = [
            'id', 'student', 'student_name', 'subject', 'subject_name', 'subject_code',
            'week_number', 'attendance_rate', 'avg_score_so_far', 'assignment_submission_rate', 'marks_trend'
        ]


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'factor_type', 'recommendation_text', 'created_at']


class RiskPredictionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    roll_no = serializers.CharField(source='student.roll_no', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    recommendations = RecommendationSerializer(many=True, read_only=True)

    class Meta:
        model = RiskPrediction
        fields = [
            'id', 'student', 'student_name', 'roll_no', 'subject', 'subject_name', 'subject_code',
            'checkpoint', 'model_used', 'risk_level', 'confidence_score', 'top_factors',
            'recommendations', 'created_at'
        ]


class InterventionNoteSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = InterventionNote
        fields = ['id', 'student', 'student_name', 'faculty', 'faculty_name', 'note', 'created_at']
