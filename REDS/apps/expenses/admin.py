from django.contrib import admin
from .models import ExpenseCategory, Expense


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'description')
    search_fields = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display    = ('title', 'category', 'amount', 'expense_date',
                       'payment_mode', 'paid_to', 'created_at')
    search_fields   = ('title', 'paid_to', 'narration')
    list_filter     = ('category', 'payment_mode', 'expense_date')
    readonly_fields = ('created_at', 'updated_at')