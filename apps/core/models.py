from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


# ======================================================
# BUSINESS PROFILE
# ======================================================

class BusinessProfile(models.Model):
    company_name        = models.CharField(max_length=200)
    company_name_urdu   = models.CharField(max_length=200, blank=True)
    logo                = models.ImageField(upload_to='logo/', blank=True, null=True)
    address             = models.TextField(blank=True)
    address_urdu        = models.TextField(blank=True)
    city                = models.CharField(max_length=100, blank=True)
    phone               = models.CharField(max_length=50, blank=True)
    email               = models.EmailField(blank=True)
    ntn_number          = models.CharField(max_length=50, blank=True)
    strn_number         = models.CharField(max_length=50, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Business Profile'
        verbose_name_plural = 'Business Profile'

    def __str__(self):
        return self.company_name


# ======================================================
# CUSTOM USER
# ======================================================

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SUPERUSER')
        return super().create_superuser(username, email, password, **extra_fields)


class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ('SUPERUSER', 'Superuser'),
        ('USER',      'User'),
    ]

    objects = CustomUserManager()

    full_name       = models.CharField(max_length=200, blank=True)
    full_name_urdu  = models.CharField(max_length=200, blank=True)
    role            = models.CharField(
                        max_length=20,
                        choices=ROLE_CHOICES,
                        default='USER'
                      )
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.role == 'SUPERUSER':
            self.is_superuser = True
            self.is_staff = True
        if self.is_superuser:
            self.role = 'SUPERUSER'
        super().save(*args, **kwargs)

    @property
    def is_superuser_role(self):
        return self.role == 'SUPERUSER'


# ======================================================
# BANK ACCOUNT
# ======================================================

class BankAccount(models.Model):
    title           = models.CharField(max_length=200)
    bank_name       = models.CharField(max_length=200)
    account_no      = models.CharField(max_length=100)
    branch          = models.CharField(max_length=200, blank=True)
    opening_balance = models.DecimalField(
                        max_digits=15,
                        decimal_places=2,
                        default=0
                      )
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} — {self.bank_name}"