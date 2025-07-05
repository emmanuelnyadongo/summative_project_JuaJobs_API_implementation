from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import User, JobCategory, Skill, Job

class AuthTests(APITestCase):
    def test_registration_and_login(self):
        url = reverse('user-register')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'worker',
            'first_name': 'Test',
            'last_name': 'User',
            'country': 'KE',
            'city': 'Nairobi',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        login_url = reverse('user-login')
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='worker', email='worker@example.com', password='pass', user_type='worker', is_verified=True)
        self.client.login(username='worker', password='pass')

    def test_user_profile(self):
        url = reverse('user-profile')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'worker')

class JobTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='client', email='client@example.com', password='pass', user_type='client', is_verified=True)
        self.category = JobCategory.objects.create(name='Web', description='Web Dev')
        self.client.force_authenticate(user=self.client_user)

    def test_create_job(self):
        url = reverse('job-list')
        data = {
            'title': 'Test Job',
            'description': 'Job description',
            'category': self.category.id,
            'job_type': 'fixed',
            'budget_min': '100.00',
            'budget_max': '500.00',
            'experience_level': 'entry',
            'is_remote': True,
            'required_skills': ['Python'],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Job')

class SkillTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass', user_type='admin', is_verified=True)
        self.client.force_authenticate(user=self.admin)

    def test_create_skill(self):
        url = reverse('skill-list')
        data = {'name': 'Django', 'category': 'technology', 'description': 'Django skill'}
        response = self.client.post(url, data)
        if response.status_code != status.HTTP_201_CREATED:
            print('Skill creation error:', response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Django')

    def test_list_skills(self):
        Skill.objects.create(name='Python', category='Programming', description='Python skill')
        url = reverse('skill-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1) 