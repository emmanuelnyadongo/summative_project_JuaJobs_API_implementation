from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import User, JobCategory, Job, Skill

class PermissionTests(APITestCase):
    def setUp(self):
        # Create different user types
        self.client_user = User.objects.create_user(
            username='client', email='client@example.com', 
            password='pass123', user_type='client', is_verified=True,
            first_name='Test', last_name='Client', country='KE', city='Nairobi'
        )
        self.worker_user = User.objects.create_user(
            username='worker', email='worker@example.com', 
            password='pass123', user_type='worker', is_verified=True,
            first_name='Test', last_name='Worker', country='KE', city='Nairobi'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', 
            password='admin123', user_type='admin', is_verified=True
        )
        
        # Create test data
        self.category = JobCategory.objects.create(name='Web Development', description='Web dev')
        self.job = Job.objects.create(
            title='Test Job',
            description='Test job description',
            category=self.category,
            client=self.client_user,
            budget_min=100,
            budget_max=500,
            job_type='fixed',
            experience_level='entry'
        )
        self.skill = Skill.objects.create(
            name='Python',
            category='technology',
            description='Python programming'
        )

    def test_client_can_create_job(self):
        """Test that clients can create jobs."""
        self.client.force_authenticate(user=self.client_user)
        url = reverse('job-list')
        data = {
            'title': 'New Job',
            'description': 'Job description',
            'category': self.category.id,
            'budget_min': '200.00',
            'budget_max': '1000.00',
            'job_type': 'fixed',
            'experience_level': 'entry',
            'is_remote': True,
            'required_skills': ['Python']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_worker_cannot_create_job(self):
        """Test that workers cannot create jobs."""
        self.client.force_authenticate(user=self.worker_user)
        url = reverse('job-list')
        data = {
            'title': 'New Job',
            'description': 'Job description',
            'category': self.category.id,
            'budget_min': '200.00',
            'budget_max': '1000.00',
            'job_type': 'fixed',
            'experience_level': 'entry'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_skill(self):
        """Test that admins can create skills."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('skill-list')
        data = {
            'name': 'Django',
            'category': 'technology',
            'description': 'Django framework'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_worker_cannot_create_skill(self):
        """Test that workers cannot create skills."""
        self.client.force_authenticate(user=self.worker_user)
        url = reverse('skill-list')
        data = {
            'name': 'Django',
            'category': 'technology',
            'description': 'Django framework'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_job_owner_can_update_job(self):
        """Test that job owners can update their jobs."""
        self.client.force_authenticate(user=self.client_user)
        url = reverse('job-detail', args=[self.job.id])
        data = {'title': 'Updated Job Title'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cannot_update_job(self):
        """Test that non-owners cannot update jobs."""
        self.client.force_authenticate(user=self.worker_user)
        url = reverse('job-detail', args=[self.job.id])
        data = {'title': 'Updated Job Title'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 