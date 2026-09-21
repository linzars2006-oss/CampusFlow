"""
SmartEdu AI - API URL Routing
Module: backend/api/urls.py
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    RegisterView, LoginView, MeView,
    StudentViewSet, FacultyViewSet, SubjectViewSet,
    BulkStudentImportView, InstitutionAnalyticsView,
    BulkAttendanceView, MarksCreateView, AssignmentScoreView,
    FacultyRiskDashboardView, InterventionNoteViewSet,
    StudentWeeklyTrendsView, StudentRiskProfileView, StudentChatView,
    SystemStatusView
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'faculty', FacultyViewSet, basename='faculty')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'interventions', InterventionNoteViewSet, basename='intervention')

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/me/', MeView.as_view(), name='me'),

    # Admin Management & Analytics
    path('admin/bulk-import/', BulkStudentImportView.as_view(), name='bulk-import'),
    path('admin/analytics/', InstitutionAnalyticsView.as_view(), name='analytics'),

    # Faculty Academic Operations & Risk Intelligence
    path('attendance/bulk/', BulkAttendanceView.as_view(), name='attendance-bulk'),
    path('marks/', MarksCreateView.as_view(), name='marks-create'),
    path('assignments/', AssignmentScoreView.as_view(), name='assignments-create'),
    path('faculty/risk-dashboard/', FacultyRiskDashboardView.as_view(), name='faculty-risk-dashboard'),

    # Student Self-Service & Longitudinal Tracking
    path('student/weekly-trends/', StudentWeeklyTrendsView.as_view(), name='student-weekly-trends'),
    path('student/my-risk/', StudentRiskProfileView.as_view(), name='student-my-risk'),
    path('student/chat/', StudentChatView.as_view(), name='student-chat'),

    # System Status & MongoDB Atlas Health
    path('system/status/', SystemStatusView.as_view(), name='system-status'),

    # Router URLs (CRUD)
    path('', include(router.urls)),
]
