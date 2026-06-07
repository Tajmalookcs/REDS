from django.db import models
from apps.core.models import CustomUser


class AccountHead(models.Model):

    TYPE_CHOICES = [
        ('ASSET',     'Asset'),
        ('LIABILITY', 'Liability'),
        ('INCOME',    'Income'),
        ('EXPENSE',   'Expense'),
        ('EQUITY',    'Equity'),
    ]

    name        = models.CharField(max_length=200)
    code        = models.CharField(max_length=20, unique=True)
    type        = models.CharField(max_length=15, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} — {self.name}"


class JournalEntry(models.Model):

    entry_date  = models.DateField()
    reference   = models.CharField(max_length=100, blank=True)
    narration   = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    created_by  = models.ForeignKey(
                    CustomUser,
                    on_delete=models.SET_NULL,
                    null=True, blank=True
                  )

    def __str__(self):
        return f"JE #{self.pk} — {self.entry_date}"

    @property
    def total_debit(self):
        return self.lines.aggregate(
            total=models.Sum('debit')
        )['total'] or 0

    @property
    def total_credit(self):
        return self.lines.aggregate(
            total=models.Sum('credit')
        )['total'] or 0


class JournalLine(models.Model):

    journal     = models.ForeignKey(
                    JournalEntry,
                    on_delete=models.CASCADE,
                    related_name='lines'
                  )
    account     = models.ForeignKey(
                    AccountHead,
                    on_delete=models.PROTECT,
                    related_name='lines'
                  )
    debit       = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit      = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    narration   = models.TextField(blank=True)

    def __str__(self):
        return f"{self.account.name} — Dr:{self.debit} Cr:{self.credit}"