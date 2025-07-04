from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from ..models import Payment, PaymentMethod, User, Job


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Basic payment method serializer."""
    
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'user', 'payment_type', 'payment_type_display',
            'provider', 'provider_display', 'account_number',
            'account_name', 'is_default', 'is_verified', 'bank_name',
            'branch_code', 'card_last_four', 'card_expiry_month',
            'card_expiry_year', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified', 'created_at', 'updated_at']


class PaymentMethodCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment methods."""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'payment_type', 'provider', 'account_number', 'account_name',
            'is_default', 'bank_name', 'branch_code', 'card_last_four',
            'card_expiry_month', 'card_expiry_year'
        ]
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        # Validate payment type specific fields
        payment_type = attrs.get('payment_type')
        provider = attrs.get('provider')
        
        if payment_type == 'bank_transfer':
            if not attrs.get('bank_name'):
                raise serializers.ValidationError(
                    "Bank name is required for bank transfer payment method."
                )
            if not attrs.get('account_number'):
                raise serializers.ValidationError(
                    "Account number is required for bank transfer payment method."
                )
        
        elif payment_type in ['credit_card', 'debit_card']:
            if not attrs.get('card_last_four'):
                raise serializers.ValidationError(
                    "Card last four digits are required for card payment method."
                )
            if not attrs.get('card_expiry_month') or not attrs.get('card_expiry_year'):
                raise serializers.ValidationError(
                    "Card expiry month and year are required for card payment method."
                )
        
        elif payment_type == 'mobile_money':
            if not attrs.get('account_number'):
                raise serializers.ValidationError(
                    "Phone number is required for mobile money payment method."
                )
        
        # Validate provider compatibility
        if payment_type == 'mobile_money' and provider not in ['mpesa', 'airtel_money', 'orange_money', 'mtn_mobile_money']:
            raise serializers.ValidationError(
                "Invalid provider for mobile money payment type."
            )
        
        elif payment_type in ['credit_card', 'debit_card'] and provider not in ['visa', 'mastercard']:
            raise serializers.ValidationError(
                "Invalid provider for card payment type."
            )
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PaymentMethodUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payment methods."""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'account_name', 'is_default', 'bank_name', 'branch_code'
        ]
    
    def validate(self, attrs):
        # Ensure only the owner can update
        user = self.context['request'].user
        if self.instance.user != user:
            raise serializers.ValidationError(
                "You can only update your own payment methods."
            )
        
        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    """Basic payment serializer."""
    
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payer_name = serializers.CharField(source='payer.get_full_name_or_username', read_only=True)
    payee_name = serializers.CharField(source='payee.get_full_name_or_username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    payment_method_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'amount', 'currency', 'payment_type',
            'payment_type_display', 'status', 'status_display', 'payer',
            'payer_name', 'payee', 'payee_name', 'job', 'job_title',
            'payment_method', 'payment_method_info', 'platform_fee',
            'net_amount', 'external_transaction_id', 'description',
            'failure_reason', 'created_at', 'updated_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'payment_id', 'payer', 'payee', 'job', 'platform_fee',
            'net_amount', 'external_transaction_id', 'failure_reason',
            'created_at', 'updated_at', 'processed_at'
        ]
    
    def get_payment_method_info(self, obj):
        if obj.payment_method:
            return {
                'id': obj.payment_method.id,
                'payment_type': obj.payment_method.get_payment_type_display(),
                'provider': obj.payment_method.get_provider_display(),
                'account_name': obj.payment_method.account_name
            }
        return None


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""
    
    class Meta:
        model = Payment
        fields = [
            'amount', 'currency', 'payment_type', 'payee', 'job',
            'payment_method', 'description'
        ]
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        # Ensure user is the payer
        attrs['payer'] = user
        
        # Validate payment method ownership
        payment_method = attrs.get('payment_method')
        if payment_method and payment_method.user != user:
            raise serializers.ValidationError(
                "You can only use your own payment methods."
            )
        
        # Validate job ownership for job payments
        job = attrs.get('job')
        if job and attrs.get('payment_type') == 'job_payment':
            if job.client != user:
                raise serializers.ValidationError(
                    "You can only make payments for your own jobs."
                )
        
        # Validate amount
        amount = attrs.get('amount')
        if amount <= 0:
            raise serializers.ValidationError(
                "Payment amount must be greater than 0."
            )
        
        # Calculate platform fee (example: 5% for job payments)
        if attrs.get('payment_type') == 'job_payment':
            attrs['platform_fee'] = amount * 0.05
        else:
            attrs['platform_fee'] = 0
        
        # Calculate net amount
        attrs['net_amount'] = amount - attrs['platform_fee']
        
        # Generate payment ID
        import uuid
        attrs['payment_id'] = str(uuid.uuid4())
        
        return attrs


class PaymentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payments."""
    
    class Meta:
        model = Payment
        fields = ['status', 'external_transaction_id', 'external_payment_data']
    
    def validate(self, attrs):
        # Only allow status updates for pending payments
        if self.instance.status != 'pending':
            raise serializers.ValidationError(
                "Can only update pending payments."
            )
        
        return attrs


class PaymentStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payment status."""
    
    class Meta:
        model = Payment
        fields = ['status']
    
    def validate_status(self, value):
        current_status = self.instance.status
        
        # Define allowed status transitions
        allowed_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'failed'],
            'completed': ['refunded'],
            'failed': ['pending'],
            'cancelled': [],
            'refunded': []
        }
        
        if value not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}."
            )
        
        return value
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        
        new_status = validated_data['status']
        
        # Update processed_at for completed payments
        if new_status == 'completed':
            instance.processed_at = timezone.now()
        
        instance.status = new_status
        instance.save()
        
        return instance


class PaymentMethodVerificationSerializer(serializers.ModelSerializer):
    """Serializer for payment method verification."""
    
    verification_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = ['verification_code']
    
    def validate_verification_code(self, value):
        # In a real implementation, you would verify the code
        # For now, we'll accept any 6-digit code
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError(
                "Verification code must be a 6-digit number."
            )
        return value
    
    def update(self, instance, validated_data):
        # Mark payment method as verified
        instance.is_verified = True
        instance.save()
        return instance


class PaymentSummarySerializer(serializers.Serializer):
    """Serializer for payment summary statistics."""
    
    total_payments = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    payment_counts_by_status = serializers.DictField()
    payment_counts_by_type = serializers.DictField()
    recent_payments = serializers.ListField()


class MpesaPaymentSerializer(serializers.Serializer):
    """Serializer for M-Pesa payment integration."""
    
    phone_number = serializers.CharField(max_length=12)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reference = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=100)
    
    def validate_phone_number(self, value):
        # Validate Kenyan phone number format
        if not value.startswith('254') and not value.startswith('+254'):
            raise serializers.ValidationError(
                "Phone number must be in format: 254XXXXXXXXX or +254XXXXXXXXX"
            )
        
        # Remove + if present
        if value.startswith('+'):
            value = value[1:]
        
        # Validate length
        if len(value) != 12:
            raise serializers.ValidationError(
                "Phone number must be 12 digits (254XXXXXXXXX)"
            )
        
        return value
    
    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Amount must be at least 1 KES"
            )
        if value > 70000:
            raise serializers.ValidationError(
                "Amount cannot exceed 70,000 KES"
            )
        return value 