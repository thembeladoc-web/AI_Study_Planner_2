"""
Attendance Views
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from datetime import datetime, timedelta

from .models import AttendanceRecord, AttendanceSummary
from .serializers import AttendanceRecordSerializer, AttendanceSummarySerializer
from apps.timetable.models import ClassSchedule, StudentCourse


class AttendanceRecordListView(generics.ListCreateAPIView):
    """List or create attendance records"""
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AttendanceRecord.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class AttendanceRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete attendance record"""
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AttendanceRecord.objects.filter(student=self.request.user)


class AttendanceSummaryListView(generics.ListAPIView):
    """List attendance summaries for current student"""
    serializer_class = AttendanceSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AttendanceSummary.objects.filter(student=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    """
    Mark attendance for a class session
    {
        "class_schedule_id": 1,
        "date": "2026-06-01",
        "status": "present",
        "check_in_time": "08:30",
        "notes": ""
    }
    """
    student = request.user
    data = request.data

    class_schedule = get_object_or_404(ClassSchedule, id=data.get('class_schedule_id'))

    # Check if student is enrolled in this course
    if not StudentCourse.objects.filter(student=student, course=class_schedule.course).exists():
        return Response(
            {'error': 'You are not enrolled in this course'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Create or update attendance record
    record, created = AttendanceRecord.objects.update_or_create(
        student=student,
        class_schedule=class_schedule,
        date=data.get('date'),
        defaults={
            'status': data.get('status', 'present'),
            'check_in_time': data.get('check_in_time'),
            'check_out_time': data.get('check_out_time'),
            'minutes_late': data.get('minutes_late', 0),
            'notes': data.get('notes', '')
        }
    )

    # Update attendance summary
    update_attendance_summary(student, class_schedule.course)

    return Response({
        'message': 'Attendance marked successfully',
        'record': AttendanceRecordSerializer(record).data
    })


def update_attendance_summary(student, course):
    """Update or create attendance summary for a student-course pair"""
    records = AttendanceRecord.objects.filter(student=student, class_schedule__course=course)

    summary, created = AttendanceSummary.objects.get_or_create(
        student=student,
        course=course,
        defaults={
            'minimum_required_percentage': 80.00,
            'warning_threshold_percentage': 85.00
        }
    )

    summary.total_sessions = records.count()
    summary.present_count = records.filter(status='present').count()
    summary.absent_count = records.filter(status='absent').count()
    summary.late_count = records.filter(status='late').count()
    summary.excused_count = records.filter(status='excused').count()

    summary.calculate_percentage()
    summary.save()

    return summary


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_alerts(request):
    """Get attendance alerts for current student"""
    student = request.user

    # Rebuild summaries so alerts always reflect the current attendance records.
    course_ids = StudentCourse.objects.filter(student=student).values_list('course_id', flat=True)
    for course_id in course_ids:
        course = ClassSchedule.objects.filter(course_id=course_id).values_list('course', flat=True).first()
        if course:
            from apps.timetable.models import Course
            update_attendance_summary(student, Course.objects.get(pk=course))

    summaries = AttendanceSummary.objects.filter(student=student).select_related('course')
    alerts = []

    for summary in summaries:
        if summary.is_below_minimum:
            alerts.append({
                'type': 'critical',
                'course': summary.course.code,
                'course_name': summary.course.name,
                'message': f"Attendance below minimum ({summary.attendance_percentage}% < {summary.minimum_required_percentage}%)",
                'attendance_percentage': summary.attendance_percentage,
                'minimum_required': summary.minimum_required_percentage,
                'sessions_needed': summary.sessions_needed_for_minimum
            })
        elif summary.is_near_threshold:
            alerts.append({
                'type': 'warning',
                'course': summary.course.code,
                'course_name': summary.course.name,
                'message': f"Attendance near threshold ({summary.attendance_percentage}%)",
                'attendance_percentage': summary.attendance_percentage,
                'warning_threshold': summary.warning_threshold_percentage,
                'sessions_needed': summary.sessions_needed_for_minimum
            })

    return Response({
        'total_alerts': len(alerts),
        'critical_count': len([a for a in alerts if a['type'] == 'critical']),
        'warning_count': len([a for a in alerts if a['type'] == 'warning']),
        'alerts': alerts
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_report(request, course_id):
    """Get detailed attendance report for a specific course"""
    student = request.user

    records = AttendanceRecord.objects.filter(
        student=student,
        class_schedule__course_id=course_id
    ).order_by('-date')

    summary = get_object_or_404(
        AttendanceSummary,
        student=student,
        course_id=course_id
    )

    # Weekly breakdown
    from collections import defaultdict
    weekly_data = defaultdict(lambda: {'present': 0, 'absent': 0, 'late': 0, 'total': 0})

    for record in records:
        week_key = record.date.strftime('%Y-W%U')
        weekly_data[week_key]['total'] += 1
        weekly_data[week_key][record.status] += 1

    return Response({
        'course': summary.course.code,
        'course_name': summary.course.name,
        'summary': AttendanceSummarySerializer(summary).data,
        'recent_records': AttendanceRecordSerializer(records[:10], many=True).data,
        'weekly_breakdown': dict(weekly_data)
    })
