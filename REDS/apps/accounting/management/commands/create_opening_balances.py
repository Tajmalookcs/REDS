from django.core.management.base import BaseCommand
from apps.accounting.models import AccountHead, JournalEntry, JournalLine
from datetime import date


class Command(BaseCommand):
    help = 'Create sample opening balance entries for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cash',
            type=float,
            default=500000,
            help='Opening cash balance (default: 500000)'
        )
        parser.add_argument(
            '--petty',
            type=float,
            default=50000,
            help='Opening petty cash balance (default: 50000)'
        )
        parser.add_argument(
            '--bank',
            type=float,
            default=300000,
            help='Opening bank balance (default: 300000)'
        )

    def handle(self, *args, **options):
        cash_balance = options['cash']
        petty_balance = options['petty']
        bank_balance = options['bank']

        self.stdout.write(self.style.WARNING('Creating Opening Balance Entries...'))

        # Get or create Equity account
        equity, created = AccountHead.objects.get_or_create(
            code='3001',
            defaults={
                'name': 'Capital/Equity',
                'type': 'EQUITY',
                'description': 'Owner equity and capital',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created equity account: 3001 - {equity.name}')
            )

        # Create opening balance entry
        total_opening = cash_balance + petty_balance + bank_balance

        je = JournalEntry.objects.create(
            entry_date=date.today(),
            reference='OB-' + date.today().strftime('%Y-%m-%d'),
            narration='Opening balance entry'
        )

        # Cash account
        cash_account = AccountHead.objects.get(code='1001')
        JournalLine.objects.create(
            journal=je,
            account=cash_account,
            debit=cash_balance,
            narration='Cash in hand opening balance'
        )

        # Petty cash account
        petty_account = AccountHead.objects.get(code='1002')
        JournalLine.objects.create(
            journal=je,
            account=petty_account,
            debit=petty_balance,
            narration='Petty cash opening balance'
        )

        # Bank account
        bank_account = AccountHead.objects.get(code='1004')
        JournalLine.objects.create(
            journal=je,
            account=bank_account,
            debit=bank_balance,
            narration='Bank opening balance'
        )

        # Equity credit
        JournalLine.objects.create(
            journal=je,
            account=equity,
            credit=total_opening,
            narration='Capital contribution'
        )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Created Journal Entry #{je.pk}')
        )
        self.stdout.write(f'  Entry Date: {je.entry_date}')
        self.stdout.write(f'  Reference: {je.reference}')
        self.stdout.write(f'  Total Debit: {je.total_debit:,.2f}')
        self.stdout.write(f'  Total Credit: {je.total_credit:,.2f}')
        self.stdout.write(
            self.style.SUCCESS('\n✓ Opening balances created successfully!')
        )
        self.stdout.write(
            self.style.WARNING('\nYou can now:')
        )
        self.stdout.write('1. View the report at: http://127.0.0.1:8000/reports/cash-bank/')
        self.stdout.write('2. Modify balances in admin: http://127.0.0.1:8000/admin/accounting/journalentry/')
