"""
Timetable App Tests
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, time, date

from apps.accounts.models import Student
from apps.timetable.models import Course, ClassSchedule, StudentCourse, Assignment, ExamSchedule


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
    return Course.objects.create(
        code='MAT201',
        name='Mathematics II',
        credits=4,
        difficulty_rating=4,
        estimated_study_hours_per_week=8
    )


@pytest.fixture
def test_schedule(test_course):
    return ClassSchedule.objects.create(
        course=test_course,
        session_type='lecture',
        day_of_week=0,  # Monday
        start_time=time(8, 0),
        end_time=time(10, 0),
        venue='Room 101',
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31)
    )


@pytest.mark.django_db
class TestCourseManagement:
    def test_create_course(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        data = {
            'code': 'PHY101',
            'name': 'Physics I',
            'credits': 3,
            'difficulty_rating': 3
        }
        response = api_client.post(reverse('course-list'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Course.objects.filter(code='PHY101').exists()

    def test_list_courses(self, api_client, test_user, test_course):
        api_client.force_authenticate(user=test_user)
        response = api_client.get(reverse('course-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1


@pytest.mark.django_db
class TestEnrollment:
    def test_enroll_in_course(self, api_client, test_user, test_course):
        api_client.force_authenticate(user=test_user)
        data = {'course_id': test_course.id, 'semester': 'semester_2'}
        response = api_client.post(reverse('enroll'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert StudentCourse.objects.filter(student=test_user, course=test_course).exists()


@pytest.mark.django_db
class TestConflictDetection:
    def test_detect_overlapping_classes(self, api_client, test_user, test_course, test_schedule):
        # Create overlapping schedule
        ClassSchedule.objects.create(
            course=test_course,
            session_type='tutorial',
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(11, 0),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31)
        )

        api_client.force_authenticate(user=test_user)
        response = api_client.get(reverse('detect-conflicts'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_conflicts'] > 0
        assert len(response.data['overlapping_classes']) > 0


@pytest.mark.django_db
class TestDashboard:
    def test_dashboard_summary(self, api_client, test_user, test_course, test_schedule):
        api_client.force_authenticate(user=test_user)
        response = api_client.get(reverse('dashboard-summary'))
        assert response.status_code == status.HTTP_200_OK
        assert 'total_courses' in response.data
