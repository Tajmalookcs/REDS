from django.db import models

# Create your models here.
from django.db import models
from apps.core.models import CustomUser


class ExpenseCategory(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Expense(models.Model):

    PAYMENT_MODE_CHOICES = [
        ('CASH',   'Cash'),
        ('BANK',   'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
    ]

    category        = models.ForeignKey(
                        ExpenseCategory,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='expenses'
                      )
    town            = models.ForeignKey(
                        'development.Town',
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='expenses'
                      )
    title           = models.CharField(max_length=200)
    amount          = models.DecimalField(max_digits=15, decimal_places=2)
    expense_date    = models.DateField()
    payment_mode    = models.CharField(
                        max_length=10,
                        choices=PAYMENT_MODE_CHOICES,
                        default='CASH'
                      )
    paid_to         = models.CharField(max_length=200, blank=True)
    cheque_no       = models.CharField(max_length=50, blank=True)
    cheque_bank     = models.CharField(max_length=100, blank=True)
    cheque_date     = models.DateField(null=True, blank=True)
    narration       = models.TextField(blank=True)
    image           = models.ImageField(upload_to='expenses/', blank=True, null=True)
    is_deleted      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    def __str__(self):
        return f"{self.title} — Rs. {self.amount}"