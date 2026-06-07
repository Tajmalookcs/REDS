from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, BusinessProfile, BankAccount


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'full_name', 'role', 'is_active', 'created_at')
    list_filter   = ('role', 'is_active')
    search_fields = ('username', 'full_name', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('REDS Info', {
            'fields': ('full_name', 'full_name_urdu', 'role')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('REDS Info', {
            'fields': ('full_name', 'full_name_urdu', 'role')
        }),
    )


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'city', 'phone', 'ntn_number')


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('title', 'bank_name', 'account_no', 'is_active')