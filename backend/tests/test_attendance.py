"""
Attendance App Tests
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, time

from apps.accounts.models import Student
from apps.timetable.models import Course, ClassSchedule, StudentCourse
from apps.attendance.models import AttendanceRecord, AttendanceSummary


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user():
    return Student.objects.create_user(
        username='teststudent',
        email='test@pace.example.com',
        password='testpass123'
    )


@pytest.fixture
def test_course():
    return Course.objects.create(code='MAT201', name='Mathematics II', credits=4)


@pytest.fixture
def test_schedule(test_course):
    return ClassSchedule.objects.create(
        course=test_course,
        session_type='lecture',
        day_of_week=0,
        start_time=time(8, 0),
        end_time=time(10, 0),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31)
    )


@pytest.mark.django_db
class TestAttendanceMarking:
    def test_mark_attendance(self, api_client, test_user, test_course, test_schedule):
        StudentCourse.objects.create(student=test_user, course=test_course)

        api_client.force_authenticate(user=test_user)
        data = {
            'class_schedule_id': test_schedule.id,
            'date': '2026-06-01',
            'status': 'present',
            'check_in_time': '08:05'
        }
        response = api_client.post(reverse('mark-attendance'), data)
        assert response.status_code == status.HTTP_200_OK
        assert AttendanceRecord.objects.filter(student=test_user).exists()

    def test_mark_attendance_unenrolled(self, api_client, test_user, test_schedule):
        api_client.force_authenticate(user=test_user)
        data = {
            'class_schedule_id': test_schedule.id,
            'date': '2026-06-01',
            'status': 'present'
        }
        response = api_client.post(reverse('mark-attendance'), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAttendanceAlerts:
    def test_attendance_alerts(self, api_client, test_user, test_course, test_schedule):
        StudentCourse.objects.create(student=test_user, course=test_course)

        for i in range(5):
            AttendanceRecord.objects.create(
                student=test_user,
                class_schedule=test_schedule,
                date=date(2026, 6, 1 + i),
                status='absent'
            )

        api_client.force_authenticate(user=test_user)
        response = api_client.get(reverse('attendance-alerts'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_alerts'] > 0
