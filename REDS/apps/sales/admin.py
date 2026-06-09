from django.contrib import admin
from .models import Booking, PaymentPlan, Receipt, Cancellation, AgentCommission


# ======================================================
# BOOKING
# ======================================================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display    = ('id', 'customer', 'plot', 'booking_date',
                       'net_price', 'total_paid', 'balance', 'status')
    search_fields   = ('customer__name', 'plot__plot_no', 'plot__block__town__name')
    list_filter     = ('status', 'booking_date', 'plot__block__town')
    readonly_fields = ('created_at', 'updated_at', 'total_paid', 'balance')


# ======================================================
# PAYMENT PLAN
# ======================================================

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display    = ('booking', 'installment_no', 'due_date',
                       'amount', 'paid_amount', 'status')
    search_fields   = ('booking__customer__name', 'booking__plot__plot_no')
    list_filter     = ('status', 'due_date')
    readonly_fields = ('created_at',)


# ======================================================
# RECEIPT
# ======================================================

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display    = ('receipt_no', 'booking', 'receipt_date',
                       'amount', 'payment_mode', 'created_at')
    search_fields   = ('receipt_no', 'booking__customer__name',
                       'booking__plot__plot_no')
    list_filter     = ('payment_mode', 'receipt_date')
    readonly_fields = ('created_at',)


# ======================================================
# CANCELLATION
# ======================================================

@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display    = ('booking', 'cancellation_date',
                       'refund_amount', 'deduction_amount', 'created_at')
    search_fields   = ('booking__customer__name', 'booking__plot__plot_no')
    list_filter     = ('cancellation_date',)
    readonly_fields = ('created_at',)


# ======================================================
# AGENT COMMISSION
# ======================================================

@admin.register(AgentCommission)
class AgentCommissionAdmin(admin.ModelAdmin):
    list_display    = ('agent', 'booking', 'commission_rate',
                       'commission_amount', 'paid_amount', 'status', 'paid_date')
    search_fields   = ('agent__name', 'booking__customer__name')
    list_filter     = ('status', 'paid_date')
    readonly_fields = ('created_at',)