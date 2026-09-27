"""
Study Groups App Tests
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import Student
from apps.timetable.models import Course, StudentCourse
from apps.study_groups.models import StudyGroup, GroupMembership


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
def test_group(test_course, test_user):
    group = StudyGroup.objects.create(
        name='Math Study Group',
        course=test_course,
        created_by=test_user,
        max_members=5,
        privacy='public'
    )
    GroupMembership.objects.create(
        group=group,
        student=test_user,
        status='active',
        role='admin'
    )
    return group


@pytest.mark.django_db
class TestGroupCreation:
    def test_create_group(self, api_client, test_user, test_course):
        StudentCourse.objects.create(student=test_user, course=test_course)

        api_client.force_authenticate(user=test_user)
        data = {
            'name': 'New Study Group',
            'course_id': test_course.id,
            'max_members': 4,
            'privacy': 'public'
        }
        response = api_client.post(reverse('study-group-list'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert StudyGroup.objects.filter(name='New Study Group').exists()


@pytest.mark.django_db
class TestGroupJoining:
    def test_join_public_group(self, api_client, test_user, test_course, test_group):
        StudentCourse.objects.create(student=test_user, course=test_course)

        other_user = Student.objects.create_user(
            username='otherstudent',
            email='other@pace.example.com',
            password='testpass123'
        )
        StudentCourse.objects.create(student=other_user, course=test_course)

        api_client.force_authenticate(user=other_user)
        response = api_client.post(reverse('join-group', kwargs={'group_id': test_group.id}))
        assert response.status_code == status.HTTP_200_OK
        assert GroupMembership.objects.filter(group=test_group, student=other_user).exists()


@pytest.mark.django_db
class TestGroupMatching:
    def test_find_study_groups(self, api_client, test_user, test_course, test_group):
        StudentCourse.objects.create(student=test_user, course=test_course)

        api_client.force_authenticate(user=test_user)
        response = api_client.get(reverse('find-study-groups'))
        assert response.status_code == status.HTTP_200_OK
        assert 'recommended_groups' in response.data
