from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    # Auth views
    UserRegistrationView,
    UserLoginView,
    user_logout_view,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
    user_profile_view,
    refresh_token_view,
    verify_token_view,
    
    # User views
    UserViewSet,
    UserProfileView,
    UserStatsView,
    
    # Job views
    JobViewSet,
    JobCategoryViewSet,
    JobApplicationViewSet,
    JobSearchView,
    JobApplicationResponseView,
    
    # Payment views
    PaymentViewSet,
    PaymentMethodViewSet,
    PaymentStatusUpdateView,
    MpesaPaymentView,
    
    # Review views
    ReviewViewSet,
    ReviewResponseView,
    UserReviewStatsView,
    
    # Notification views
    NotificationViewSet,
    NotificationMarkReadView,
    
    # Location views
    LocationViewSet,
    LocationTreeView,
    
    # Skill views
    SkillViewSet,
    UserSkillViewSet,
)

# Create router and register viewsets
router = DefaultRouter()

# User routes
router.register(r'users', UserViewSet, basename='user')

# Job routes
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'job-categories', JobCategoryViewSet, basename='job-category')
router.register(r'applications', JobApplicationViewSet, basename='application')

# Payment routes
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')

# Review routes
router.register(r'reviews', ReviewViewSet, basename='review')

# Notification routes
router.register(r'notifications', NotificationViewSet, basename='notification')

# Location routes
router.register(r'locations', LocationViewSet, basename='location')

# Skill routes
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'user-skills', UserSkillViewSet, basename='user-skill')

# URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication URLs
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', user_logout_view, name='user-logout'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('auth/password/reset/', PasswordResetView.as_view(), name='password-reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/profile/', user_profile_view, name='user-profile'),
    path('auth/token/refresh/', refresh_token_view, name='token-refresh'),
    path('auth/token/verify/', verify_token_view, name='token-verify'),
    
    # JWT token URLs
    path('auth/token/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Job search
    path('jobs/search/', JobSearchView.as_view(), name='job-search'),
    
    # Job application response
    path('applications/<int:pk>/respond/', JobApplicationResponseView.as_view(), name='application-respond'),
    
    # Payment specific routes
    path('payments/<int:pk>/status/', PaymentStatusUpdateView.as_view(), name='payment-status-update'),
    path('payments/mpesa/', MpesaPaymentView.as_view(), name='mpesa-payment'),
    
    # Review response
    path('reviews/<int:pk>/respond/', ReviewResponseView.as_view(), name='review-respond'),
    
    # User review stats
    path('users/<int:pk>/review-stats/', UserReviewStatsView.as_view(), name='user-review-stats'),
    
    # Notification mark read
    path('notifications/<int:pk>/mark-read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    
    # Location tree
    path('locations/tree/', LocationTreeView.as_view(), name='location-tree'),
    
    # User profile and stats
    path('users/profile/', UserProfileView.as_view(), name='user-profile-detail'),
    path('users/<int:pk>/stats/', UserStatsView.as_view(), name='user-stats'),
] 