from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Q
from ..models import Payment, PaymentMethod
from ..serializers import (
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentStatusUpdateSerializer,
    PaymentMethodSerializer,
    PaymentMethodCreateSerializer,
    PaymentMethodUpdateSerializer,
    MpesaPaymentSerializer,
)
from ..permissions import IsPaymentOwner, CanMakePayments


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Payment ViewSet for managing payments.
    
    list: GET /api/payments/
    create: POST /api/payments/
    retrieve: GET /api/payments/{id}/
    update: PUT /api/payments/{id}/
    partial_update: PATCH /api/payments/{id}/
    destroy: DELETE /api/payments/{id}/
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsPaymentOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_type', 'currency']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user role
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(payer=self.request.user) | Q(payee=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the payer when creating a payment."""
        serializer.save(payer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Get current user's payments."""
        payments = Payment.objects.filter(payer=request.user)
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = PaymentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def received_payments(self, request):
        """Get payments received by current user."""
        payments = Payment.objects.filter(payee=request.user)
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = PaymentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    Payment Method ViewSet for managing payment methods.
    
    list: GET /api/payment-methods/
    create: POST /api/payment-methods/
    retrieve: GET /api/payment-methods/{id}/
    update: PUT /api/payment-methods/{id}/
    partial_update: PATCH /api/payment-methods/{id}/
    destroy: DELETE /api/payment-methods/{id}/
    """
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['payment_type', 'provider', 'is_verified', 'is_default']
    ordering_fields = ['created_at']
    ordering = ['-is_default', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentMethodCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PaymentMethodUpdateSerializer
        return PaymentMethodSerializer
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating a payment method."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a payment method."""
        payment_method = self.get_object()
        
        # In a real implementation, you would verify the payment method
        # For now, we'll just mark it as verified
        payment_method.is_verified = True
        payment_method.save()
        
        return Response({'message': 'Payment method verified successfully.'})
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set a payment method as default."""
        payment_method = self.get_object()
        payment_method.is_default = True
        payment_method.save()
        
        return Response({'message': 'Payment method set as default.'})


class PaymentStatusUpdateView(generics.UpdateAPIView):
    """
    Payment status update view.
    
    PATCH /api/payments/{id}/status/
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(payer=self.request.user)


class MpesaPaymentView(generics.GenericAPIView):
    """
    M-Pesa payment integration view.
    
    POST /api/payments/mpesa/
    """
    serializer_class = MpesaPaymentSerializer
    permission_classes = [IsAuthenticated, CanMakePayments]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In a real implementation, you would integrate with M-Pesa API
        # For now, we'll just create a mock payment
        
        from ..models import Payment
        import uuid
        
        payment = Payment.objects.create(
            payment_id=str(uuid.uuid4()),
            amount=serializer.validated_data['amount'],
            currency='KES',
            payment_type='job_payment',
            payer=request.user,
            payee=request.user,  # Mock payee
            description=serializer.validated_data['description'],
            status='processing'
        )
        
        # Simulate payment processing
        import threading
        import time
        
        def process_payment():
            time.sleep(2)  # Simulate processing time
            payment.status = 'completed'
            payment.save()
        
        thread = threading.Thread(target=process_payment)
        thread.start()
        
        return Response({
            'message': 'M-Pesa payment initiated successfully.',
            'payment_id': payment.payment_id,
            'status': payment.status
        }, status=status.HTTP_202_ACCEPTED) 