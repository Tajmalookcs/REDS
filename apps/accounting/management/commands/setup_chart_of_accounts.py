from django.core.management.base import BaseCommand
from apps.accounting.models import AccountHead, JournalEntry, JournalLine
from django.utils import timezone
from datetime import date


class Command(BaseCommand):
    help = 'Set up initial chart of accounts and opening balances'

    def handle(self, *args, **options):
        # Create Account Heads if they don't exist
        accounts = [
            # ASSETS
            {
                'code': '1001',
                'name': 'Cash in Hand',
                'type': 'ASSET',
                'description': 'Physical cash held',
            },
            {
                'code': '1002',
                'name': 'Petty Cash',
                'type': 'ASSET',
                'description': 'Small cash expenses',
            },
            {
                'code': '1003',
                'name': 'Cheques in Hand',
                'type': 'ASSET',
                'description': 'Cheques received but not cleared',
            },
            {
                'code': '1004',
                'name': 'Bank Account',
                'type': 'ASSET',
                'description': 'Main bank account',
            },
            # INCOME
            {
                'code': '4001',
                'name': 'Sales Revenue',
                'type': 'INCOME',
                'description': 'Revenue from plot sales',
            },
            {
                'code': '4002',
                'name': 'Commission Income',
                'type': 'INCOME',
                'description': 'Agent commissions received',
            },
            # EXPENSES
            {
                'code': '5001',
                'name': 'Salaries & Wages',
                'type': 'EXPENSE',
                'description': 'Employee salaries and wages',
            },
            {
                'code': '5002',
                'name': 'Rent Expense',
                'type': 'EXPENSE',
                'description': 'Office and property rent',
            },
            {
                'code': '5003',
                'name': 'Utilities',
                'type': 'EXPENSE',
                'description': 'Electricity, water, gas',
            },
            {
                'code': '5004',
                'name': 'Office Supplies',
                'type': 'EXPENSE',
                'description': 'Stationery and office supplies',
            },
            {
                'code': '5005',
                'name': 'Travel & Transportation',
                'type': 'EXPENSE',
                'description': 'Travel and transportation costs',
            },
            {
                'code': '5006',
                'name': 'Marketing & Advertising',
                'type': 'EXPENSE',
                'description': 'Marketing and advertising expenses',
            },
            {
                'code': '5007',
                'name': 'Professional Fees',
                'type': 'EXPENSE',
                'description': 'Legal, accounting, consulting fees',
            },
            {
                'code': '5008',
                'name': 'Depreciation',
                'type': 'EXPENSE',
                'description': 'Depreciation of assets',
            },
            # LIABILITY
            {
                'code': '2001',
                'name': 'Accounts Payable',
                'type': 'LIABILITY',
                'description': 'Amounts owed to suppliers',
            },
            {
                'code': '2002',
                'name': 'Loans Payable',
                'type': 'LIABILITY',
                'description': 'Bank loans and borrowings',
            },
            # EQUITY
            {
                'code': '3001',
                'name': 'Capital/Equity',
                'type': 'EQUITY',
                'description': 'Owner equity and capital',
            },
            {
                'code': '3002',
                'name': 'Retained Earnings',
                'type': 'EQUITY',
                'description': 'Accumulated profits',
            },
        ]

        created_count = 0
        for acc in accounts:
            account, created = AccountHead.objects.get_or_create(
                code=acc['code'],
                defaults={
                    'name': acc['name'],
                    'type': acc['type'],
                    'description': acc['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created account: {acc["code"]} - {acc["name"]}')
                )
                created_count += 1
            else:
                self.stdout.write(f'→ Account exists: {acc["code"]} - {acc["name"]}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Chart of Accounts setup complete! ({created_count} new accounts created)')
        )
        self.stdout.write(
            self.style.WARNING('\nNext Steps:')
        )
        self.stdout.write('1. Go to Django Admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('2. Navigate to Accounting > Journal Entries')
        self.stdout.write('3. Create opening balance entries for your cash accounts')
        self.stdout.write('4. Create expense entries to populate P&L statement')
