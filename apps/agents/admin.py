from django.contrib import admin
from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display    = ('name', 'phone', 'cnic', 'city', 'created_at')
    search_fields   = ('name', 'phone', 'cnic')
    list_filter     = ('city', 'created_at')
    readonly_fields = ('created_at', 'updated_at')