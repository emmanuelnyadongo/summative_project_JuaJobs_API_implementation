from rest_framework import permissions
from django.utils.translation import gettext_lazy as _


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsJobOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow job owners to edit their jobs.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the job owner
        return obj.client == request.user


class IsApplicationOwnerOrJobOwner(permissions.BasePermission):
    """
    Custom permission for job applications.
    - Application owner can read and update their own applications
    - Job owner can read and respond to applications for their jobs
    """
    
    def has_object_permission(self, request, view, obj):
        # Application owner can do anything with their application
        if obj.worker == request.user:
            return True
        
        # Job owner can read and respond to applications
        if obj.job.client == request.user:
            if request.method in permissions.SAFE_METHODS:
                return True
            # Job owner can only update status and add client message
            if request.method in ['PATCH', 'PUT']:
                allowed_fields = ['status', 'client_message']
                return all(field in allowed_fields for field in request.data.keys())
        
        return False


class IsClientOnly(permissions.BasePermission):
    """
    Custom permission to only allow clients to perform certain actions.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client


class IsWorkerOnly(permissions.BasePermission):
    """
    Custom permission to only allow workers to perform certain actions.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_worker


class IsAdminOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to perform certain actions.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow verified users to perform certain actions.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified


class IsActiveWorker(permissions.BasePermission):
    """
    Custom permission to only allow active workers to perform certain actions.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_worker and request.user.is_active_worker


class IsPaymentOwner(permissions.BasePermission):
    """
    Custom permission for payments.
    - Payer can read and update their payments
    - Payee can read payments they received
    """
    
    def has_object_permission(self, request, view, obj):
        # Payer can do anything with their payments
        if obj.payer == request.user:
            return True
        
        # Payee can read payments they received
        if obj.payee == request.user and request.method in permissions.SAFE_METHODS:
            return True
        
        return False


class IsReviewOwnerOrReviewed(permissions.BasePermission):
    """
    Custom permission for reviews.
    - Reviewer can read and update their own reviews
    - Reviewed user can read reviews about them and respond
    """
    
    def has_object_permission(self, request, view, obj):
        # Reviewer can do anything with their reviews
        if obj.reviewer == request.user:
            return True
        
        # Reviewed user can read reviews about them and respond
        if obj.reviewed_user == request.user:
            if request.method in permissions.SAFE_METHODS:
                return True
            # Can only add response
            if request.method in ['PATCH', 'PUT'] and 'response' in request.data:
                return True
        
        return False


class IsNotificationOwner(permissions.BasePermission):
    """
    Custom permission to only allow notification owners to access their notifications.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsUserSkillOwner(permissions.BasePermission):
    """
    Custom permission to only allow user skill owners to manage their skills.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanPostJobs(permissions.BasePermission):
    """
    Custom permission to check if user can post jobs.
    - Must be a client
    - Must be verified (optional, can be configured)
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not request.user.is_client:
            return False
        
        # Optional: require verification for posting jobs
        # Uncomment the line below if you want to require verification
        # return request.user.is_verified
        
        return True


class CanApplyForJobs(permissions.BasePermission):
    """
    Custom permission to check if user can apply for jobs.
    - Must be a worker
    - Must be active
    - Must be verified (optional, can be configured)
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not request.user.is_worker:
            return False
        
        if not request.user.is_active_worker:
            return False
        
        # Optional: require verification for applying to jobs
        # Uncomment the line below if you want to require verification
        # return request.user.is_verified
        
        return True


class CanMakePayments(permissions.BasePermission):
    """
    Custom permission to check if user can make payments.
    - Must be authenticated
    - Must have verified payment methods (optional)
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Optional: require verified payment methods
        # Uncomment the lines below if you want to require verified payment methods
        # verified_payment_methods = request.user.payment_methods.filter(is_verified=True)
        # return verified_payment_methods.exists()
        
        return True


class IsJobParticipant(permissions.BasePermission):
    """
    Custom permission to check if user is a participant in a job.
    - Client or assigned worker can access job details
    """
    
    def has_object_permission(self, request, view, obj):
        # Job owner can access
        if obj.client == request.user:
            return True
        
        # Assigned worker can access
        if obj.assigned_worker == request.user:
            return True
        
        # Admin can access
        if request.user.is_admin:
            return True
        
        return False


class IsJobApplicationParticipant(permissions.BasePermission):
    """
    Custom permission to check if user is a participant in a job application.
    - Worker who applied can access
    - Client who posted the job can access
    """
    
    def has_object_permission(self, request, view, obj):
        # Worker who applied can access
        if obj.worker == request.user:
            return True
        
        # Client who posted the job can access
        if obj.job.client == request.user:
            return True
        
        # Admin can access
        if request.user.is_admin:
            return True
        
        return False


class ReadOnlyIfNotOwner(permissions.BasePermission):
    """
    Custom permission that allows read access to all users,
    but write access only to the owner.
    """
    
    def has_permission(self, request, view):
        # Allow all authenticated users to read
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return True
    
    def has_object_permission(self, request, view, obj):
        # Allow read access to all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Allow write access only to the owner
        return obj.user == request.user


class IsPublicOrOwner(permissions.BasePermission):
    """
    Custom permission that allows access to public objects or owners.
    """
    
    def has_object_permission(self, request, view, obj):
        # Allow access if object is public
        if hasattr(obj, 'is_public') and obj.is_public:
            return True
        
        # Allow access to owner
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Allow access to admin
        if request.user.is_admin:
            return True
        
        return False 