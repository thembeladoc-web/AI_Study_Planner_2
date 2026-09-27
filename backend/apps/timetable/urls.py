"""
Timetable URL Configuration
"""
from django.urls import path
from .views import (
    CourseListView, CourseDetailView,
    ClassScheduleListView, ClassScheduleDetailView,
    MyCoursesView, EnrollCourseView, UnenrollCourseView,
    AssignmentListView, AssignmentDetailView, UpcomingAssignmentsView,
    ExamScheduleListView, EventListCreateView, EventDetailView,
    EventParticipantListCreateView, EventParticipantDetailView,
    detect_conflicts, dashboard_summary
)

urlpatterns = [
    # Events and participants
    path('events/', EventListCreateView.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('events/<int:event_id>/participants/', EventParticipantListCreateView.as_view(), name='event-participant-list'),
    path('events/<int:event_id>/participants/<int:pk>/', EventParticipantDetailView.as_view(), name='event-participant-detail'),
    # Courses
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),

    # Class Schedules
    path('schedules/', ClassScheduleListView.as_view(), name='schedule-list'),
    path('schedules/<int:pk>/', ClassScheduleDetailView.as_view(), name='schedule-detail'),

    # Student Enrollments
    path('my-courses/', MyCoursesView.as_view(), name='my-courses'),
    path('enroll/', EnrollCourseView.as_view(), name='enroll'),
    path('unenroll/<int:pk>/', UnenrollCourseView.as_view(), name='unenroll'),

    # Assignments
    path('assignments/', AssignmentListView.as_view(), name='assignment-list'),
    path('assignments/<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/upcoming/', UpcomingAssignmentsView.as_view(), name='upcoming-assignments'),

    # Exams
    path('exams/', ExamScheduleListView.as_view(), name='exam-list'),

    # Utility APIs
    path('conflicts/', detect_conflicts, name='detect-conflicts'),
    path('dashboard/', dashboard_summary, name='dashboard-summary'),
]
