"""
Accounts App Tests
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import Student


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user():
    return Student.objects.create_user(
        username='teststudent',
        email='test@pace.example.com',
        password='testpass123',
        first_name='Test',
        last_name='Student',
        student_number='R20260001',
        program='BSc IT',
        year_of_study=3
    )


@pytest.mark.django_db
class TestRegistration:
    def test_successful_registration(self, api_client):
        data = {
            'username': 'newstudent',
            'email': 'new@pace.example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Student',
            'student_number': 'R20260002',
            'program': 'BSc IT',
            'year_of_study': 2,
            'study_preference': 'morning'
        }
        response = api_client.post(reverse('register'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert Student.objects.filter(username='newstudent').exists()

    def test_password_mismatch(self, api_client):
        data = {
            'username': 'newstudent',
            'email': 'new@pace.example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'New',
            'last_name': 'Student'
        }
        response = api_client.post(reverse('register'), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    def test_successful_login(self, api_client, test_user):
        data = {
            'username': 'teststudent',
            'password': 'testpass123'
        }
        response = api_client.post(reverse('login'), data)
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data

    def test_invalid_credentials(self, api_client):
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        response = api_client.post(reverse('login'), data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProfile:
    def test_get_profile(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        response = api_client.get(reverse('profile'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'teststudent'

    def test_update_profile(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        data = {'phone': '0712345678', 'study_preference': 'evening'}
        response = api_client.patch(reverse('profile'), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone'] == '0712345678'
