from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.sales.models import Receipt, Booking, Cancellation, AgentCommission
from apps.expenses.models import Expense
from apps.land.models import ContractPaymentSchedule
from apps.accounting.journal_auto import (
    journal_on_receipt,
    journal_on_booking,
    journal_on_cancellation,
    journal_on_landlord_payment,
    journal_on_expense,
    journal_on_commission_paid,
)


# ─────────────────────────────────────────
# RECEIPT SAVED
# ─────────────────────────────────────────
@receiver(post_save, sender=Receipt)
def receipt_saved(sender, instance, created, **kwargs):
    if created:
        journal_on_receipt(instance, user=instance.created_by)


# ─────────────────────────────────────────
# BOOKING SAVED
# ─────────────────────────────────────────
@receiver(post_save, sender=Booking)
def booking_saved(sender, instance, created, **kwargs):
    if created:
        journal_on_booking(instance, user=instance.created_by)


# ─────────────────────────────────────────
# CANCELLATION SAVED
# ─────────────────────────────────────────
@receiver(post_save, sender=Cancellation)
def cancellation_saved(sender, instance, created, **kwargs):
    if created:
        journal_on_cancellation(instance, user=instance.created_by)


# ─────────────────────────────────────────
# LANDLORD PAYMENT SAVED
# ─────────────────────────────────────────
@receiver(post_save, sender=ContractPaymentSchedule)
def landlord_payment_saved(sender, instance, created, **kwargs):
    if instance.status == 'PAID' and instance.paid_amount:
        journal_on_landlord_payment(instance)


# ─────────────────────────────────────────
# EXPENSE SAVED
# ─────────────────────────────────────────
@receiver(post_save, sender=Expense)
def expense_saved(sender, instance, created, **kwargs):
    if created:
        journal_on_expense(instance, user=instance.created_by)


# ─────────────────────────────────────────
# AGENT COMMISSION PAID
# ─────────────────────────────────────────
@receiver(post_save, sender=AgentCommission)
def commission_saved(sender, instance, created, **kwargs):
    if instance.status == 'PAID':
        journal_on_commission_paid(instance, user=instance.created_by)