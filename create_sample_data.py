#!/usr/bin/env python
"""
Script to create sample data for the JuaJobs API.
Run this script to populate the database with test data.
"""

import os
import sys
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jua_jobs.settings')
django.setup()

from api.models import (
    User, JobCategory, Job, Skill, Location, 
    JobApplication, Payment, Review, Notification
)


def create_sample_data():
    """Create sample data for testing."""
    print("Creating sample data...")
    
    # Create job categories
    categories = [
        {'name': 'Web Development', 'description': 'Frontend and backend web development'},
        {'name': 'Mobile Development', 'description': 'iOS and Android app development'},
        {'name': 'Design', 'description': 'Graphic design and UI/UX'},
        {'name': 'Writing', 'description': 'Content writing and copywriting'},
        {'name': 'Marketing', 'description': 'Digital marketing and SEO'},
        {'name': 'Data Science', 'description': 'Data analysis and machine learning'},
    ]
    
    job_categories = []
    for cat_data in categories:
        category, created = JobCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        job_categories.append(category)
        if created:
            print(f"Created category: {category.name}")
    
    # Create skills
    skills_data = [
        {'name': 'Python', 'category': 'Programming'},
        {'name': 'JavaScript', 'category': 'Programming'},
        {'name': 'React', 'category': 'Frontend'},
        {'name': 'Django', 'category': 'Backend'},
        {'name': 'UI/UX Design', 'category': 'Design'},
        {'name': 'Content Writing', 'category': 'Writing'},
        {'name': 'SEO', 'category': 'Marketing'},
        {'name': 'Data Analysis', 'category': 'Data Science'},
    ]
    
    skills = []
    for skill_data in skills_data:
        skill, created = Skill.objects.get_or_create(
            name=skill_data['name'],
            defaults={
                'category': skill_data['category'],
                'description': f'{skill_data["name"]} skill',
                'is_active': True
            }
        )
        skills.append(skill)
        if created:
            print(f"Created skill: {skill.name}")
    
    # Create locations
    locations = [
        {'name': 'Nairobi', 'location_type': 'city', 'country_code': 'KE'},
        {'name': 'Mombasa', 'location_type': 'city', 'country_code': 'KE'},
        {'name': 'Kisumu', 'location_type': 'city', 'country_code': 'KE'},
    ]
    
    for loc_data in locations:
        location, created = Location.objects.get_or_create(
            name=loc_data['name'],
            defaults={
                'location_type': loc_data['location_type'],
                'country_code': loc_data['country_code'],
                'is_active': True
            }
        )
        if created:
            print(f"Created location: {location.name}")
    
    # Create users (clients and workers)
    users_data = [
        {
            'username': 'client1',
            'email': 'client1@example.com',
            'first_name': 'John',
            'last_name': 'Client',
            'user_type': 'client',
            'is_verified': True,
            'company_name': 'Tech Solutions Ltd',
        },
        {
            'username': 'client2',
            'email': 'client2@example.com',
            'first_name': 'Jane',
            'last_name': 'Business',
            'user_type': 'client',
            'is_verified': True,
            'company_name': 'Digital Marketing Co',
        },
        {
            'username': 'worker1',
            'email': 'worker1@example.com',
            'first_name': 'Alice',
            'last_name': 'Developer',
            'user_type': 'worker',
            'is_verified': True,
            'is_active_worker': True,
            'hourly_rate': Decimal('25.00'),
            'bio': 'Experienced web developer with 5+ years of experience.',
        },
        {
            'username': 'worker2',
            'email': 'worker2@example.com',
            'first_name': 'Bob',
            'last_name': 'Designer',
            'user_type': 'worker',
            'is_verified': True,
            'is_active_worker': True,
            'hourly_rate': Decimal('30.00'),
            'bio': 'Creative UI/UX designer passionate about user experience.',
        },
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"Created user: {user.username}")
        users.append(user)
    
    # Create jobs
    jobs_data = [
        {
            'title': 'Website Development for E-commerce',
            'description': 'Need a modern e-commerce website with payment integration.',
            'category': job_categories[0],  # Web Development
            'client': users[0],  # client1
            'job_type': 'fixed',
            'budget_min': Decimal('500.00'),
            'budget_max': Decimal('2000.00'),
            'experience_level': 'intermediate',
            'is_remote': True,
            'required_skills': ['Python', 'Django', 'JavaScript'],
        },
        {
            'title': 'Mobile App for Food Delivery',
            'description': 'Looking for a React Native developer to build a food delivery app.',
            'category': job_categories[1],  # Mobile Development
            'client': users[1],  # client2
            'job_type': 'hourly',
            'budget_min': Decimal('20.00'),
            'budget_max': Decimal('50.00'),
            'hourly_rate': Decimal('35.00'),
            'experience_level': 'expert',
            'is_remote': True,
            'required_skills': ['React', 'JavaScript'],
        },
        {
            'title': 'Logo Design for Startup',
            'description': 'Need a professional logo design for our new startup.',
            'category': job_categories[2],  # Design
            'client': users[0],  # client1
            'job_type': 'fixed',
            'budget_min': Decimal('100.00'),
            'budget_max': Decimal('300.00'),
            'experience_level': 'entry',
            'is_remote': True,
            'required_skills': ['UI/UX Design'],
        },
    ]
    
    jobs = []
    for job_data in jobs_data:
        required_skills = job_data.pop('required_skills')
        job = Job.objects.create(**job_data)
        job.required_skills = required_skills
        job.save()
        jobs.append(job)
        print(f"Created job: {job.title}")
    
    # Create job applications
    applications_data = [
        {
            'job': jobs[0],
            'worker': users[2],  # worker1
            'cover_letter': 'I have extensive experience with Django and e-commerce development.',
            'proposed_rate': Decimal('1500.00'),
            'estimated_duration': 40,
        },
        {
            'job': jobs[1],
            'worker': users[3],  # worker2
            'cover_letter': 'I specialize in React Native and have built several delivery apps.',
            'proposed_rate': Decimal('40.00'),
            'estimated_duration': 80,
        },
        {
            'job': jobs[2],
            'worker': users[3],  # worker2
            'cover_letter': 'I am a creative designer with experience in logo design.',
            'proposed_rate': Decimal('200.00'),
            'estimated_duration': 10,
        },
    ]
    
    for app_data in applications_data:
        application, created = JobApplication.objects.get_or_create(
            job=app_data['job'],
            worker=app_data['worker'],
            defaults=app_data
        )
        if created:
            print(f"Created application: {application.worker.username} -> {application.job.title}")
    
    # Create some reviews
    reviews_data = [
        {
            'reviewer': users[0],  # client1
            'reviewed_user': users[2],  # worker1
            'job': jobs[0],
            'rating': 5,
            'title': 'Excellent work!',
            'comment': 'Very professional and delivered on time.',
            'review_type': 'client_to_worker',
        },
        {
            'reviewer': users[2],  # worker1
            'reviewed_user': users[0],  # client1
            'job': jobs[0],
            'rating': 4,
            'title': 'Great client',
            'comment': 'Clear requirements and good communication.',
            'review_type': 'worker_to_client',
        },
    ]
    
    for review_data in reviews_data:
        review, created = Review.objects.get_or_create(
            reviewer=review_data['reviewer'],
            reviewed_user=review_data['reviewed_user'],
            job=review_data['job'],
            defaults=review_data
        )
        if created:
            print(f"Created review: {review.reviewer.username} -> {review.reviewed_user.username}")
    
    # Create notifications
    notifications_data = [
        {
            'user': users[2],  # worker1
            'notification_type': 'job_application',
            'title': 'New job application',
            'message': 'Your application for "Website Development" has been received.',
            'priority': 'medium',
        },
        {
            'user': users[0],  # client1
            'notification_type': 'new_application',
            'title': 'New application received',
            'message': 'You have received a new application for your job.',
            'priority': 'high',
        },
    ]
    
    for notif_data in notifications_data:
        notification = Notification.objects.create(**notif_data)
        print(f"Created notification: {notification.title}")
    
    print("\nSample data creation completed!")
    print(f"Created {len(job_categories)} categories")
    print(f"Created {len(skills)} skills")
    print(f"Created {len(users)} users")
    print(f"Created {len(jobs)} jobs")
    print(f"Created {len(applications_data)} job applications")
    print(f"Created {len(reviews_data)} reviews")
    print(f"Created {len(notifications_data)} notifications")


if __name__ == '__main__':
    create_sample_data() 