"""Admin-only API routes for the Pace management dashboard."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .admin_views import (
    AdminAssignmentViewSet,
    AdminAttendanceViewSet,
    AdminCourseViewSet,
    AdminExamViewSet,
    AdminScheduleViewSet,
    AdminStatsView,
    AdminStudentViewSet,
    AdminStudyGroupViewSet,
)

router = DefaultRouter()
router.register('users', AdminStudentViewSet, basename='admin-users')
router.register('courses', AdminCourseViewSet, basename='admin-courses')
router.register('schedules', AdminScheduleViewSet, basename='admin-schedules')
router.register('assignments', AdminAssignmentViewSet, basename='admin-assignments')
router.register('exams', AdminExamViewSet, basename='admin-exams')
router.register('study-groups', AdminStudyGroupViewSet, basename='admin-study-groups')
router.register('attendance', AdminAttendanceViewSet, basename='admin-attendance')

urlpatterns = [
    path('stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('', include(router.urls)),
]
