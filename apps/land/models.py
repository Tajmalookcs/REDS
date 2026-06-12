from django.db import models
from apps.core.models import CustomUser, BankAccount


# ======================================================
# LANDLORD
# ======================================================

class Landlord(models.Model):
    name        = models.CharField(max_length=200)
    name_urdu   = models.CharField(max_length=200, blank=True)
    cnic        = models.CharField(max_length=20, blank=True)
    phone       = models.CharField(max_length=50, blank=True)
    address     = models.TextField(blank=True)
    city        = models.CharField(max_length=100, blank=True)
    is_deleted  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    created_by  = models.ForeignKey(
                    CustomUser,
                    on_delete=models.SET_NULL,
                    null=True, blank=True
                  )

    def __str__(self):
        return self.name


# ======================================================
# LAND CONTRACT
# ======================================================

class LandContract(models.Model):

    TYPE_CHOICES = [
        ('CASH',        'Cash'),
        ('INSTALLMENT', 'Installment'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE',    'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    AREA_UNIT_CHOICES = [
        ('MARLA', 'Marla'),
        ('KANAL', 'Kanal'),
        ('SQFT',  'Square Feet'),
        ('ACRE',  'Acre'),
    ]

    landlord        = models.ForeignKey(
                        Landlord,
                        on_delete=models.PROTECT,
                        related_name='contracts'
                      )
    title           = models.CharField(max_length=200)
    location        = models.TextField(blank=True)
    total_area      = models.DecimalField(max_digits=15, decimal_places=2)
    area_unit       = models.CharField(
                        max_length=10,
                        choices=AREA_UNIT_CHOICES,
                        default='MARLA'
                      )
    total_amount    = models.DecimalField(max_digits=15, decimal_places=2)
    contract_type   = models.CharField(
                        max_length=15,
                        choices=TYPE_CHOICES,
                        default='CASH'
                      )
    start_date      = models.DateField()
    duration_years  = models.PositiveIntegerField(default=0)
    status          = models.CharField(
                        max_length=15,
                        choices=STATUS_CHOICES,
                        default='ACTIVE'
                      )
    notes           = models.TextField(blank=True)
    contract_pdf    = models.FileField(upload_to='contracts/pdf/', null=True, blank=True)
    is_deleted      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    def __str__(self):
        return f"{self.title} — {self.landlord.name}"


# ======================================================
# CONTRACT PAYMENT SCHEDULE
# ======================================================

class ContractPaymentSchedule(models.Model):

    PAYMENT_MODE_CHOICES = [
        ('CASH',   'Cash'),
        ('BANK',   'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID',    'Paid'),
        ('PARTIAL', 'Partial'),
    ]

    CHEQUE_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CLEARED', 'Cleared'),
        ('BOUNCED', 'Bounced'),
    ]

    contract        = models.ForeignKey(
                        LandContract,
                        on_delete=models.CASCADE,
                        related_name='schedules'
                      )
    installment_no  = models.PositiveIntegerField()
    amount          = models.DecimalField(max_digits=15, decimal_places=2)
    due_date        = models.DateField()
    paid_date       = models.DateField(null=True, blank=True)
    paid_amount     = models.DecimalField(
                        max_digits=15,
                        decimal_places=2,
                        default=0
                      )
    payment_mode    = models.CharField(
                        max_length=10,
                        choices=PAYMENT_MODE_CHOICES,
                        blank=True
                      )
    bank_account    = models.ForeignKey(
                        BankAccount,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )
    cheque_no       = models.CharField(max_length=50, blank=True)
    cheque_bank     = models.CharField(max_length=100, blank=True)
    cheque_status   = models.CharField(
                        max_length=10,
                        choices=CHEQUE_STATUS_CHOICES,
                        blank=True
                      )
    status          = models.CharField(
                        max_length=10,
                        choices=STATUS_CHOICES,
                        default='PENDING'
                      )
    narration       = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    def __str__(self):
        return f"Installment {self.installment_no} — {self.contract.title}"