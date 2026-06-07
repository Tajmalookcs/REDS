from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.sales.models import Receipt
from apps.accounting.models import AccountHead, JournalEntry, JournalLine


@receiver(post_save, sender=Receipt)
def create_receipt_journal_entry(sender, instance, created, **kwargs):
    """
    Automatically create journal entry when a receipt is recorded.
    This ensures cash/bank/cheques are properly recorded in the accounting system.
    """
    if created and not instance.is_deleted:
        try:
            # Determine which account to debit based on payment mode
            if instance.payment_mode == 'CASH':
                debit_account_code = '1001'  # Cash in Hand
            elif instance.payment_mode == 'BANK':
                debit_account_code = '1004'  # Bank Account
            elif instance.payment_mode == 'CHEQUE':
                debit_account_code = '1003'  # Cheques in Hand
            else:
                return  # Unknown payment mode

            # Get or create the accounts
            debit_account = AccountHead.objects.get(code=debit_account_code)
            credit_account = AccountHead.objects.get(code='4001')  # Sales Revenue

            # Create journal entry
            je = JournalEntry.objects.create(
                entry_date=instance.receipt_date,
                reference=instance.receipt_no,
                narration=f"Receipt {instance.receipt_no} - {instance.booking.customer.name}"
            )

            # Debit Cash/Bank/Cheques
            JournalLine.objects.create(
                journal=je,
                account=debit_account,
                debit=instance.amount,
                narration=f"Cash received for booking #{instance.booking.id}"
            )

            # Credit Sales Revenue
            JournalLine.objects.create(
                journal=je,
                account=credit_account,
                credit=instance.amount,
                narration=f"Sales revenue from {instance.booking.customer.name}"
            )

        except AccountHead.DoesNotExist:
            # Account not found - just skip journal entry creation
            pass
        except Exception as e:
            # Log error but don't fail the receipt creation
            print(f"Error creating journal entry for receipt {instance.receipt_no}: {str(e)}")
