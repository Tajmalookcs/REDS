from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display    = ('name', 'contact', 'cnic', 'city', 'created_at')
    search_fields   = ('name', 'contact', 'cnic')
    list_filter     = ('city', 'created_at')
    readonly_fields = ('created_at', 'updated_at')