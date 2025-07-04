from django.db import models
from django.utils.translation import gettext_lazy as _
from .user import User
from .job import Job


class PaymentMethod(models.Model):
    """
    Payment methods available for users.
    """
    class PaymentType(models.TextChoices):
        MOBILE_MONEY = 'mobile_money', _('Mobile Money')
        BANK_TRANSFER = 'bank_transfer', _('Bank Transfer')
        CREDIT_CARD = 'credit_card', _('Credit Card')
        DEBIT_CARD = 'debit_card', _('Debit Card')
        DIGITAL_WALLET = 'digital_wallet', _('Digital Wallet')
        CASH = 'cash', _('Cash')
    
    class Provider(models.TextChoices):
        MPESA = 'mpesa', _('M-Pesa')
        AIRTEL_MONEY = 'airtel_money', _('Airtel Money')
        ORANGE_MONEY = 'orange_money', _('Orange Money')
        MTN_MOBILE_MONEY = 'mtn_mobile_money', _('MTN Mobile Money')
        VISA = 'visa', _('Visa')
        MASTERCARD = 'mastercard', _('Mastercard')
        PAYPAL = 'paypal', _('PayPal')
        STRIPE = 'stripe', _('Stripe')
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_methods',
        help_text=_('User who owns this payment method')
    )
    
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        help_text=_('Type of payment method')
    )
    
    provider = models.CharField(
        max_length=30,
        choices=Provider.choices,
        help_text=_('Payment provider')
    )
    
    account_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Account number or phone number')
    )
    
    account_name = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Account holder name')
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text=_('Whether this is the default payment method')
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether this payment method is verified')
    )
    
    # Additional details for different payment types
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Bank name for bank transfers')
    )
    
    branch_code = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('Bank branch code')
    )
    
    card_last_four = models.CharField(
        max_length=4,
        blank=True,
        help_text=_('Last four digits of card')
    )
    
    card_expiry_month = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Card expiry month')
    )
    
    card_expiry_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Card expiry year')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['payment_type']),
            models.Index(fields=['provider']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_payment_type_display()} ({self.provider})"
    
    def save(self, *args, **kwargs):
        """Ensure only one default payment method per user."""
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Payment transactions for jobs and services.
    """
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        CANCELLED = 'cancelled', _('Cancelled')
        REFUNDED = 'refunded', _('Refunded')
    
    class PaymentType(models.TextChoices):
        JOB_PAYMENT = 'job_payment', _('Job Payment')
        ESCROW_DEPOSIT = 'escrow_deposit', _('Escrow Deposit')
        ESCROW_RELEASE = 'escrow_release', _('Escrow Release')
        REFUND = 'refund', _('Refund')
        WITHDRAWAL = 'withdrawal', _('Withdrawal')
        PLATFORM_FEE = 'platform_fee', _('Platform Fee')
    
    # Transaction Details
    payment_id = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Unique payment identifier')
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_('Payment amount')
    )
    
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text=_('Payment currency')
    )
    
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        help_text=_('Type of payment')
    )
    
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text=_('Payment status')
    )
    
    # Parties Involved
    payer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments_made',
        help_text=_('User making the payment')
    )
    
    payee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments_received',
        help_text=_('User receiving the payment')
    )
    
    # Related Job
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='payments',
        blank=True,
        null=True,
        help_text=_('Related job')
    )
    
    # Payment Method
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_('Payment method used')
    )
    
    # Platform Fee
    platform_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text=_('Platform fee amount')
    )
    
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_('Net amount after fees')
    )
    
    # External Payment Details
    external_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('External payment provider transaction ID')
    )
    
    external_payment_data = models.JSONField(
        default=dict,
        help_text=_('Additional data from external payment provider')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When payment was processed')
    )
    
    # Additional Information
    description = models.TextField(
        blank=True,
        help_text=_('Payment description')
    )
    
    failure_reason = models.TextField(
        blank=True,
        help_text=_('Reason for payment failure')
    )
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_type']),
            models.Index(fields=['payer']),
            models.Index(fields=['payee']),
            models.Index(fields=['created_at']),
            models.Index(fields=['external_transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.payment_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        """Calculate net amount before saving."""
        if not self.net_amount:
            self.net_amount = self.amount - self.platform_fee
        super().save(*args, **kwargs)
    
    @property
    def is_completed(self):
        """Check if payment is completed."""
        return self.status == self.PaymentStatus.COMPLETED
    
    @property
    def is_failed(self):
        """Check if payment failed."""
        return self.status == self.PaymentStatus.FAILED
    
    @property
    def is_pending(self):
        """Check if payment is pending."""
        return self.status == self.PaymentStatus.PENDING
    
    def mark_as_completed(self):
        """Mark payment as completed."""
        from django.utils import timezone
        self.status = self.PaymentStatus.COMPLETED
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])
    
    def mark_as_failed(self, reason=""):
        """Mark payment as failed."""
        self.status = self.PaymentStatus.FAILED
        self.failure_reason = reason
        self.save(update_fields=['status', 'failure_reason']) 