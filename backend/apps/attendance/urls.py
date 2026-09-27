"""
Attendance URL Configuration
"""
from django.urls import path
from .views import (
    AttendanceRecordListView, AttendanceRecordDetailView,
    AttendanceSummaryListView,
    mark_attendance, attendance_alerts, attendance_report
)

urlpatterns = [
    path('records/', AttendanceRecordListView.as_view(), name='attendance-record-list'),
    path('records/<int:pk>/', AttendanceRecordDetailView.as_view(), name='attendance-record-detail'),
    path('summaries/', AttendanceSummaryListView.as_view(), name='attendance-summary-list'),
    path('mark/', mark_attendance, name='mark-attendance'),
    path('alerts/', attendance_alerts, name='attendance-alerts'),
    path('report/<int:course_id>/', attendance_report, name='attendance-report'),
]
