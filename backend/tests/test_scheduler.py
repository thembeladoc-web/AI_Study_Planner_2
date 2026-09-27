"""
Scheduler App Tests - AI Study Plan Generation
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, time, datetime

from apps.accounts.models import Student
from apps.timetable.models import Course, ClassSchedule, StudentCourse
from apps.scheduler.models import StudyPlan, StudySession


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user():
    return Student.objects.create_user(
        username='teststudent',
        email='test@pace.example.com',
        password='testpass123',
        study_preference='morning',
        max_study_hours_per_day=6
    )


@pytest.fixture
def test_course():
    return Course.objects.create(
        code='MAT201',
        name='Mathematics II',
        credits=4,
        difficulty_rating=4
    )


@pytest.fixture
def enrolled_course(test_user, test_course):
    StudentCourse.objects.create(
        student=test_user,
        course=test_course,
        semester='semester_2',
        academic_year='2026'
    )
    return test_course


@pytest.mark.django_db
class TestStudyPlanGeneration:
    def test_generate_study_plan(self, api_client, test_user, enrolled_course):
        api_client.force_authenticate(user=test_user)
        data = {
            'week_start': '2026-06-01',
            'week_end': '2026-06-07',
            'preferences': {
                'max_hours_per_day': 6,
                'min_break_minutes': 30
            }
        }
        response = api_client.post(reverse('generate-study-plan'), data)
        assert response.status_code == status.HTTP_200_OK
        assert 'study_plan' in response.data
        assert response.data['sessions_created'] > 0
        assert response.data['solver_status'] in ['OPTIMAL', 'FEASIBLE']

    def test_study_plan_with_no_courses(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        data = {
            'week_start': '2026-06-01',
            'week_end': '2026-06-07'
        }
        response = api_client.post(reverse('generate-study-plan'), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data


@pytest.mark.django_db
class TestStudySessionManagement:
    def test_mark_session_complete(self, api_client, test_user, enrolled_course):
        plan = StudyPlan.objects.create(
            student=test_user,
            week_start=date(2026, 6, 1),
            week_end=date(2026, 6, 7)
        )
        session = StudySession.objects.create(
            study_plan=plan,
            course=enrolled_course,
            day_of_week=0,
            start_time=time(14, 0),
            end_time=time(15, 30),
            duration_minutes=90,
            session_type='deep_study'
        )

        api_client.force_authenticate(user=test_user)
        data = {'actual_duration_minutes': 90, 'notes': 'Completed chapter 3'}
        response = api_client.post(
            reverse('mark-complete', kwargs={'session_id': session.id}),
            data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['session']['is_completed'] is True


@pytest.mark.django_db
class TestStudyPlanStats:
    def test_plan_statistics(self, api_client, test_user, enrolled_course):
        plan = StudyPlan.objects.create(
            student=test_user,
            week_start=date(2026, 6, 1),
            week_end=date(2026, 6, 7)
        )
        StudySession.objects.create(
            study_plan=plan,
            course=enrolled_course,
            day_of_week=0,
            start_time=time(14, 0),
            end_time=time(15, 0),
            duration_minutes=60,
            is_completed=True,
            actual_duration_minutes=60
        )

        api_client.force_authenticate(user=test_user)
        response = api_client.get(reverse('study-plan-stats', kwargs={'plan_id': plan.id}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completion_rate'] == 100.0
