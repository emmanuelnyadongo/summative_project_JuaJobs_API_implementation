from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from ..models import Job, JobCategory, JobApplication
from ..serializers import (
    JobSerializer,
    JobCreateSerializer,
    JobUpdateSerializer,
    JobDetailSerializer,
    JobCategorySerializer,
    JobApplicationSerializer,
    JobApplicationCreateSerializer,
    JobApplicationUpdateSerializer,
    JobApplicationResponseSerializer,
    JobSearchSerializer,
)
from ..permissions import (
    IsJobOwnerOrReadOnly,
    IsApplicationOwnerOrJobOwner,
    CanPostJobs,
    CanApplyForJobs,
    IsJobParticipant,
    IsJobApplicationParticipant,
)
from rest_framework.permissions import IsAuthenticated


class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Job Category ViewSet for viewing job categories.
    
    list: GET /api/job-categories/
    retrieve: GET /api/job-categories/{id}/
    """
    queryset = JobCategory.objects.filter(is_active=True)
    serializer_class = JobCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'job_count']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, pk=None):
        """Get jobs in a specific category."""
        category = self.get_object()
        jobs = category.jobs.filter(status='open')
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = JobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)


class JobViewSet(viewsets.ModelViewSet):
    """
    Job ViewSet for managing jobs.
    
    list: GET /api/jobs/
    create: POST /api/jobs/
    retrieve: GET /api/jobs/{id}/
    update: PUT /api/jobs/{id}/
    partial_update: PATCH /api/jobs/{id}/
    destroy: DELETE /api/jobs/{id}/
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsJobOwnerOrReadOnly]
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), CanPostJobs()]
        return [IsAuthenticated(), IsJobOwnerOrReadOnly()]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'job_type', 'experience_level', 'category', 'is_remote', 'is_featured', 'is_urgent']
    search_fields = ['title', 'description', 'location', 'required_skills', 'preferred_skills']
    ordering_fields = ['created_at', 'budget_min', 'budget_max', 'views_count', 'applications_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return JobUpdateSerializer
        elif self.action == 'retrieve':
            return JobDetailSerializer
        return JobSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by budget range
        min_budget = self.request.query_params.get('min_budget')
        if min_budget:
            queryset = queryset.filter(budget_min__gte=min_budget)
        
        max_budget = self.request.query_params.get('max_budget')
        if max_budget:
            queryset = queryset.filter(budget_max__lte=max_budget)
        
        # Filter by skills
        skills = self.request.query_params.getlist('skills')
        if skills:
            for skill in skills:
                queryset = queryset.filter(
                    Q(required_skills__contains=[skill]) | 
                    Q(preferred_skills__contains=[skill])
                )
        
        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(
                Q(location__icontains=location) | 
                Q(city__icontains=location) | 
                Q(country__icontains=location)
            )
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the client when creating a job."""
        serializer.save(client=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving a job."""
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_jobs(self, request):
        """Get current user's jobs."""
        jobs = Job.objects.filter(client=request.user)
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = JobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def open_jobs(self, request):
        """Get all open jobs."""
        jobs = Job.objects.filter(status='open')
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = JobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured_jobs(self, request):
        """Get featured jobs."""
        jobs = Job.objects.filter(is_featured=True, status='open')
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = JobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgent_jobs(self, request):
        """Get urgent jobs."""
        jobs = Job.objects.filter(is_urgent=True, status='open')
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = JobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_worker(self, request, pk=None):
        """Assign a worker to a job."""
        job = self.get_object()
        worker_id = request.data.get('worker_id')
        
        if not worker_id:
            return Response(
                {'error': 'Worker ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from ..models import User
            worker = User.objects.get(id=worker_id, user_type='worker')
        except User.DoesNotExist:
            return Response(
                {'error': 'Worker not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        job.assigned_worker = worker
        job.status = 'in_progress'
        job.save()
        
        return Response({'message': 'Worker assigned successfully.'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a job as completed."""
        job = self.get_object()
        
        if job.status != 'in_progress':
            return Response(
                {'error': 'Job must be in progress to be completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.status = 'completed'
        job.save()
        
        return Response({'message': 'Job completed successfully.'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a job."""
        job = self.get_object()
        
        if job.status not in ['open', 'in_progress']:
            return Response(
                {'error': 'Job cannot be cancelled in its current status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.status = 'cancelled'
        job.save()
        
        return Response({'message': 'Job cancelled successfully.'})


class JobSearchView(generics.ListAPIView):
    """
    Advanced job search view.
    
    GET /api/jobs/search/
    """
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'job_type', 'experience_level', 'category', 'is_remote']
    search_fields = ['title', 'description', 'location', 'required_skills', 'preferred_skills']
    ordering_fields = ['created_at', 'budget_min', 'budget_max', 'views_count', 'applications_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Job.objects.filter(status='open')
        
        # Parse search parameters
        search_serializer = JobSearchSerializer(data=self.request.query_params)
        search_serializer.is_valid(raise_exception=True)
        
        # Apply filters
        if search_serializer.validated_data.get('q'):
            query = search_serializer.validated_data['q']
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )
        
        if search_serializer.validated_data.get('category'):
            queryset = queryset.filter(category=search_serializer.validated_data['category'])
        
        if search_serializer.validated_data.get('job_type'):
            queryset = queryset.filter(job_type=search_serializer.validated_data['job_type'])
        
        if search_serializer.validated_data.get('experience_level'):
            queryset = queryset.filter(experience_level=search_serializer.validated_data['experience_level'])
        
        if search_serializer.validated_data.get('min_budget'):
            queryset = queryset.filter(budget_min__gte=search_serializer.validated_data['min_budget'])
        
        if search_serializer.validated_data.get('max_budget'):
            queryset = queryset.filter(budget_max__lte=search_serializer.validated_data['max_budget'])
        
        if search_serializer.validated_data.get('is_remote') is not None:
            queryset = queryset.filter(is_remote=search_serializer.validated_data['is_remote'])
        
        if search_serializer.validated_data.get('location'):
            location = search_serializer.validated_data['location']
            queryset = queryset.filter(
                Q(location__icontains=location) |
                Q(city__icontains=location) |
                Q(country__icontains=location)
            )
        
        if search_serializer.validated_data.get('skills'):
            skills = search_serializer.validated_data['skills']
            for skill in skills:
                queryset = queryset.filter(
                    Q(required_skills__contains=[skill]) | 
                    Q(preferred_skills__contains=[skill])
                )
        
        if search_serializer.validated_data.get('featured'):
            queryset = queryset.filter(is_featured=True)
        
        if search_serializer.validated_data.get('urgent'):
            queryset = queryset.filter(is_urgent=True)
        
        return queryset


class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    Job Application ViewSet for managing job applications.
    
    list: GET /api/applications/
    create: POST /api/applications/
    retrieve: GET /api/applications/{id}/
    update: PUT /api/applications/{id}/
    partial_update: PATCH /api/applications/{id}/
    destroy: DELETE /api/applications/{id}/
    """
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsApplicationOwnerOrJobOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'job']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return JobApplicationUpdateSerializer
        return JobApplicationSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user role
        if self.request.user.is_worker:
            # Workers see their own applications
            queryset = queryset.filter(worker=self.request.user)
        elif self.request.user.is_client:
            # Clients see applications for their jobs
            queryset = queryset.filter(job__client=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the worker when creating an application."""
        serializer.save(worker=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """Get current user's applications."""
        if not request.user.is_worker:
            return Response(
                {'error': 'Only workers can view their applications.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        applications = JobApplication.objects.filter(worker=request.user)
        page = self.paginate_queryset(applications)
        if page is not None:
            serializer = JobApplicationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def job_applications(self, request):
        """Get applications for a specific job."""
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response(
                {'error': 'Job ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job = Job.objects.get(id=job_id, client=request.user)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found or access denied.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        applications = JobApplication.objects.filter(job=job)
        page = self.paginate_queryset(applications)
        if page is not None:
            serializer = JobApplicationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class JobApplicationResponseView(generics.UpdateAPIView):
    """
    Job application response view for clients to respond to applications.
    
    PATCH /api/applications/{id}/respond/
    """
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationResponseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return JobApplication.objects.filter(job__client=self.request.user) 