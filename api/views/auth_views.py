from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ..models import User
from ..serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    UserSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': _('User registered successfully.'),
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    User login endpoint.
    
    POST /api/auth/login/
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last active
        user.save(update_fields=['last_active'])
        
        return Response({
            'message': _('Login successful.'),
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout_view(request):
    """
    User logout endpoint.
    
    POST /api/auth/logout/
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': _('Logout successful.')
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': _('Invalid token.')
        }, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(generics.GenericAPIView):
    """
    Password change endpoint.
    
    POST /api/auth/password/change/
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': _('Password changed successfully.')
        }, status=status.HTTP_200_OK)


class PasswordResetView(generics.GenericAPIView):
    """
    Password reset request endpoint.
    
    POST /api/auth/password/reset/
    """
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # In a real implementation, you would send a password reset email
        # For now, we'll just return a success message
        # You can integrate with Django's password reset functionality here
        
        return Response({
            'message': _('Password reset email sent successfully.')
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Password reset confirmation endpoint.
    
    POST /api/auth/password/reset/confirm/
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In a real implementation, you would validate the token and uid
        # and reset the password
        # For now, we'll just return a success message
        
        return Response({
            'message': _('Password reset successfully.')
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """
    Get current user profile.
    
    GET /api/auth/profile/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token_view(request):
    """
    Refresh access token.
    
    POST /api/auth/token/refresh/
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error': _('Refresh token is required.')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        return Response({
            'access': str(token.access_token),
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': _('Invalid refresh token.')
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_token_view(request):
    """
    Verify access token.
    
    POST /api/auth/token/verify/
    """
    # If the request reaches this point, the token is valid
    # because the IsAuthenticated permission class validates it
    return Response({
        'message': _('Token is valid.'),
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK) 