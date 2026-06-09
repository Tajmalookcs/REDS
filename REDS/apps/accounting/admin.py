from django.contrib import admin
from .models import AccountHead, JournalEntry, JournalLine


@admin.register(AccountHead)
class AccountHeadAdmin(admin.ModelAdmin):
    list_display    = ('code', 'name', 'type', 'is_active')
    search_fields   = ('code', 'name')
    list_filter     = ('type', 'is_active')


class JournalLineInline(admin.TabularInline):
    model  = JournalLine
    extra  = 2


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display    = ('id', 'entry_date', 'reference',
                       'total_debit', 'total_credit', 'created_at')
    search_fields   = ('reference', 'narration')
    list_filter     = ('entry_date',)
    readonly_fields = ('created_at', 'total_debit', 'total_credit')
    inlines         = [JournalLineInline]