from django.core.management.base import BaseCommand
from apps.sales.models import Receipt
from apps.accounting.models import AccountHead, JournalEntry, JournalLine


class Command(BaseCommand):
    help = 'Create journal entries for existing receipts that dont have one'

    def handle(self, *args, **options):
        receipts = Receipt.objects.filter(is_deleted=False)
        created_count = 0
        existing_count = 0

        for receipt in receipts:
            # Check if journal entry already exists for this receipt
            je_exists = JournalEntry.objects.filter(reference=receipt.receipt_no).exists()

            if je_exists:
                existing_count += 1
                continue

            try:
                # Determine which account to debit based on payment mode
                if receipt.payment_mode == 'CASH':
                    debit_account_code = '1001'  # Cash in Hand
                elif receipt.payment_mode == 'BANK':
                    debit_account_code = '1004'  # Bank Account
                elif receipt.payment_mode == 'CHEQUE':
                    debit_account_code = '1003'  # Cheques in Hand
                else:
                    continue

                # Get the accounts
                debit_account = AccountHead.objects.get(code=debit_account_code)
                credit_account = AccountHead.objects.get(code='4001')  # Sales Revenue

                # Create journal entry
                je = JournalEntry.objects.create(
                    entry_date=receipt.receipt_date,
                    reference=receipt.receipt_no,
                    narration=f"Receipt {receipt.receipt_no} - {receipt.booking.customer.name}"
                )

                # Debit Cash/Bank/Cheques
                JournalLine.objects.create(
                    journal=je,
                    account=debit_account,
                    debit=receipt.amount,
                    narration=f"Cash received for booking #{receipt.booking.id}"
                )

                # Credit Sales Revenue
                JournalLine.objects.create(
                    journal=je,
                    account=credit_account,
                    credit=receipt.amount,
                    narration=f"Sales revenue from {receipt.booking.customer.name}"
                )

                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created entry for receipt {receipt.receipt_no}')
                )

            except AccountHead.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ Missing account for receipt {receipt.receipt_no}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error for receipt {receipt.receipt_no}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Summary:')
        )
        self.stdout.write(f'  Created: {created_count} journal entries')
        self.stdout.write(f'  Already exist: {existing_count} entries')
        self.stdout.write(
            self.style.WARNING('\nNow cash in hand will be updated in Cash & Bank Position report!')
        )
