from django.db import models
from apps.core.models import CustomUser
from apps.development.models import Plot
from apps.customers.models import Customer
from apps.agents.models import Agent


# ======================================================
# BOOKING
# ======================================================

class Booking(models.Model):

    STATUS_CHOICES = [
        ('ACTIVE',     'Active'),
        ('COMPLETED',  'Completed'),
        ('CANCELLED',  'Cancelled'),
    ]

    plot            = models.ForeignKey(
                        Plot,
                        on_delete=models.PROTECT,
                        related_name='bookings'
                      )
    customer        = models.ForeignKey(
                        Customer,
                        on_delete=models.PROTECT,
                        related_name='bookings'
                      )
    agent           = models.ForeignKey(
                        Agent,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='bookings'
                      )
    booking_date    = models.DateField()
    total_price     = models.DecimalField(max_digits=15, decimal_places=2)
    discount        = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_price       = models.DecimalField(max_digits=15, decimal_places=2)
    down_payment    = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status          = models.CharField(
                        max_length=15,
                        choices=STATUS_CHOICES,
                        default='ACTIVE'
                      )
    possession      = models.BooleanField(default=False)
    registry_no     = models.CharField(max_length=100, blank=True)
    inteqal_no      = models.CharField(max_length=100, blank=True)
    notes           = models.TextField(blank=True)
    is_deleted      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    def __str__(self):
        return f"Booking #{self.pk} — {self.customer.name} — Plot {self.plot.plot_no}"

    @property
    def booking_no(self):
        return f"BK-{self.pk:04d}"

    @property
    def total_paid(self):
        return self.receipts.filter(
            is_deleted=False
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def balance(self):
        return self.net_price - self.total_paid


# ======================================================
# PAYMENT PLAN
# ======================================================

class PaymentPlan(models.Model):

    STATUS_CHOICES = [
        ('PENDING',  'Pending'),
        ('PAID',     'Paid'),
        ('PARTIAL',  'Partial'),
        ('OVERDUE',  'Overdue'),
    ]

    booking         = models.ForeignKey(
                        Booking,
                        on_delete=models.CASCADE,
                        related_name='payment_plans'
                      )
    installment_no  = models.PositiveIntegerField()
    due_date        = models.DateField()
    amount          = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount     = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_date       = models.DateField(null=True, blank=True)
    status          = models.CharField(
                        max_length=10,
                        choices=STATUS_CHOICES,
                        default='PENDING'
                      )
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['installment_no']

    def __str__(self):
        return f"Installment #{self.installment_no} — Booking #{self.booking.pk}"


# ======================================================
# RECEIPT
# ======================================================

class Receipt(models.Model):

    PAYMENT_MODE_CHOICES = [
        ('CASH',   'Cash'),
        ('BANK',   'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
    ]

    CHEQUE_STATUS_CHOICES = [
        ('PENDING', 'Pending Clearance'),
        ('CLEARED', 'Cleared'),
        ('BOUNCED', 'Bounced'),
    ]

    booking         = models.ForeignKey(
                        Booking,
                        on_delete=models.PROTECT,
                        related_name='receipts'
                      )
    payment_plan    = models.ForeignKey(
                        PaymentPlan,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='receipts'
                      )
    receipt_no      = models.CharField(max_length=50, unique=True)
    receipt_date    = models.DateField()
    amount          = models.DecimalField(max_digits=15, decimal_places=2)
    payment_mode    = models.CharField(
                        max_length=10,
                        choices=PAYMENT_MODE_CHOICES,
                        default='CASH'
                      )
    cheque_no       = models.CharField(max_length=100, blank=True)
    cheque_bank     = models.CharField(max_length=200, blank=True)
    cheque_date     = models.DateField(null=True, blank=True)
    cheque_status   = models.CharField(
                        max_length=10,
                        choices=CHEQUE_STATUS_CHOICES,
                        default='PENDING',
                        blank=True
                      )
    bank_account    = models.CharField(max_length=100, blank=True)
    narration       = models.TextField(blank=True)
    is_deleted      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    def __str__(self):
        return f"Receipt {self.receipt_no} — Rs. {self.amount}"

    @property
    def date(self):
        return self.receipt_date

    @property
    def remarks(self):
        return self.narration


# ======================================================
# CANCELLATION
# ======================================================

class Cancellation(models.Model):

    booking             = models.OneToOneField(
                            Booking,
                            on_delete=models.PROTECT,
                            related_name='cancellation'
                          )
    cancellation_date   = models.DateField()
    reason              = models.TextField(blank=True)
    refund_amount       = models.DecimalField(
                            max_digits=15,
                            decimal_places=2,
                            default=0
                          )
    deduction_amount    = models.DecimalField(
                            max_digits=15,
                            decimal_places=2,
                            default=0
                          )
    notes               = models.TextField(blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    created_by          = models.ForeignKey(
                            CustomUser,
                            on_delete=models.SET_NULL,
                            null=True, blank=True
                          )
    refund_paid         = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    refund_paid_date    = models.DateField(null=True, blank=True)
    refund_payment_mode = models.CharField(max_length=15, blank=True)
    refund_notes        = models.TextField(blank=True)

    @property
    def refund_status(self):
        if self.refund_amount <= 0:
            return 'NO_REFUND'
        if self.refund_paid >= self.refund_amount:
            return 'PAID'
        if self.refund_paid > 0:
            return 'PARTIAL'
        return 'PENDING'

    def __str__(self):
        return f"Cancellation — Booking #{self.booking.pk}"


# ======================================================
# REFUND RECEIPT
# ======================================================

class RefundReceipt(models.Model):

    PAYMENT_MODE_CHOICES = [
        ('CASH',          'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHEQUE',        'Cheque'),
    ]

    cancellation    = models.OneToOneField(
                        Cancellation,
                        on_delete=models.PROTECT,
                        related_name='refund_receipt'
                      )
    receipt_no      = models.CharField(max_length=50, unique=True)
    receipt_date    = models.DateField()
    amount          = models.DecimalField(max_digits=15, decimal_places=2)
    payment_mode    = models.CharField(max_length=15, choices=PAYMENT_MODE_CHOICES, default='CASH')
    cheque_no       = models.CharField(max_length=100, blank=True)
    cheque_bank     = models.CharField(max_length=200, blank=True)
    cheque_date     = models.DateField(null=True, blank=True)
    bank_account    = models.CharField(max_length=100, blank=True)
    narration       = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    def __str__(self):
        return f"Refund Receipt {self.receipt_no} — Rs. {self.amount}"


# ======================================================
# AGENT COMMISSION
# ======================================================

class AgentCommission(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID',    'Paid'),
    ]

    booking         = models.OneToOneField(
                        Booking,
                        on_delete=models.PROTECT,
                        related_name='commission'
                      )
    agent           = models.ForeignKey(
                        Agent,
                        on_delete=models.PROTECT,
                        related_name='commissions'
                      )
    commission_rate = models.DecimalField(
                        max_digits=5,
                        decimal_places=2,
                        default=0,
                        help_text='Percentage %'
                      )
    commission_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount     = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status          = models.CharField(
                        max_length=10,
                        choices=STATUS_CHOICES,
                        default='PENDING'
                      )
    paid_date       = models.DateField(null=True, blank=True)
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    def __str__(self):
        return f"Commission — {self.agent.name} — Booking #{self.booking.pk}"
    
# ======================================================
# PLOT TRANSFER
# ======================================================

class PlotTransfer(models.Model):

    TRANSFER_TYPE_CHOICES = [
        ('SELF',       'Self (Same Buyer)'),
        ('NEW_PERSON', 'New Person'),
    ]

    STATUS_CHOICES = [
        ('PENDING',   'Pending'),
        ('COMPLETED', 'Completed'),
    ]

    transfer_no       = models.CharField(max_length=30, unique=True, editable=False)
    booking           = models.ForeignKey(
                            Booking,
                            on_delete=models.PROTECT,
                            related_name='transfers'
                        )
    transfer_type     = models.CharField(
                            max_length=15,
                            choices=TRANSFER_TYPE_CHOICES,
                            default='SELF'
                        )
    from_customer     = models.ForeignKey(
                            'customers.Customer',
                            on_delete=models.PROTECT,
                            related_name='transfers_from'
                        )
    to_customer       = models.ForeignKey(
                            'customers.Customer',
                            on_delete=models.PROTECT,
                            related_name='transfers_to'
                        )
    transfer_date     = models.DateField()
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes             = models.TextField(blank=True)
    status            = models.CharField(
                            max_length=10,
                            choices=STATUS_CHOICES,
                            default='PENDING'
                        )
    created_at        = models.DateTimeField(auto_now_add=True)
    created_by        = models.ForeignKey(
                            'core.CustomUser',
                            on_delete=models.SET_NULL,
                            null=True, blank=True
                        )

    def save(self, *args, **kwargs):
        if not self.transfer_no:
            from datetime import date
            year  = date.today().year
            last  = PlotTransfer.objects.filter(
                        transfer_no__startswith=f'TRF-{year}-'
                    ).count()
            self.transfer_no = f'TRF-{year}-{str(last + 1).zfill(3)}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transfer_no} — {self.from_customer.name} → {self.to_customer.name}"