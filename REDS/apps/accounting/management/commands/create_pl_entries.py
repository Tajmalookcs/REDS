from django.core.management.base import BaseCommand
from apps.accounting.models import AccountHead, JournalEntry, JournalLine
from datetime import date


class Command(BaseCommand):
    help = 'Create sample P&L entries for testing profit & loss statement'

    def add_arguments(self, parser):
        parser.add_argument(
            '--revenue',
            type=float,
            default=1000000,
            help='Sales revenue amount (default: 1000000)'
        )
        parser.add_argument(
            '--salaries',
            type=float,
            default=150000,
            help='Salaries expense (default: 150000)'
        )
        parser.add_argument(
            '--rent',
            type=float,
            default=50000,
            help='Rent expense (default: 50000)'
        )
        parser.add_argument(
            '--utilities',
            type=float,
            default=15000,
            help='Utilities expense (default: 15000)'
        )
        parser.add_argument(
            '--marketing',
            type=float,
            default=100000,
            help='Marketing expense (default: 100000)'
        )

    def handle(self, *args, **options):
        revenue = options['revenue']
        salaries = options['salaries']
        rent = options['rent']
        utilities = options['utilities']
        marketing = options['marketing']

        self.stdout.write(self.style.WARNING('Creating Sample P&L Entries...'))

        # Get accounts
        try:
            sales_account = AccountHead.objects.get(code='4001')
            salaries_account = AccountHead.objects.get(code='5001')
            rent_account = AccountHead.objects.get(code='5002')
            utilities_account = AccountHead.objects.get(code='5003')
            marketing_account = AccountHead.objects.get(code='5006')
            cash_account = AccountHead.objects.get(code='1001')
        except AccountHead.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Missing account: {e}')
            )
            return

        # Create Sales Entry
        je_sales = JournalEntry.objects.create(
            entry_date=date.today(),
            reference='SALES-' + date.today().strftime('%Y-%m-%d'),
            narration='Monthly sales revenue'
        )
        JournalLine.objects.create(
            journal=je_sales,
            account=cash_account,
            debit=revenue,
            narration='Cash from sales'
        )
        JournalLine.objects.create(
            journal=je_sales,
            account=sales_account,
            credit=revenue,
            narration='Sales revenue'
        )

        # Create Expense Entries
        je_expenses = JournalEntry.objects.create(
            entry_date=date.today(),
            reference='EXP-' + date.today().strftime('%Y-%m-%d'),
            narration='Monthly operating expenses'
        )

        total_expenses = salaries + rent + utilities + marketing

        # Salaries
        JournalLine.objects.create(
            journal=je_expenses,
            account=salaries_account,
            debit=salaries,
            narration='Employee salaries'
        )

        # Rent
        JournalLine.objects.create(
            journal=je_expenses,
            account=rent_account,
            debit=rent,
            narration='Office rent'
        )

        # Utilities
        JournalLine.objects.create(
            journal=je_expenses,
            account=utilities_account,
            debit=utilities,
            narration='Utilities and services'
        )

        # Marketing
        JournalLine.objects.create(
            journal=je_expenses,
            account=marketing_account,
            debit=marketing,
            narration='Advertising and marketing'
        )

        # Credit to cash for expenses
        JournalLine.objects.create(
            journal=je_expenses,
            account=cash_account,
            credit=total_expenses,
            narration='Expense payments'
        )

        net_profit = revenue - total_expenses

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Created Sales Entry #{je_sales.pk}')
        )
        self.stdout.write(f'  Revenue: {revenue:,.2f}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Created Expense Entry #{je_expenses.pk}')
        )
        self.stdout.write(f'  Salaries: {salaries:,.2f}')
        self.stdout.write(f'  Rent: {rent:,.2f}')
        self.stdout.write(f'  Utilities: {utilities:,.2f}')
        self.stdout.write(f'  Marketing: {marketing:,.2f}')
        self.stdout.write(f'  Total Expenses: {total_expenses:,.2f}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Calculated Net Profit: {net_profit:,.2f}')
        )
        self.stdout.write(
            self.style.WARNING('\nYou can now:')
        )
        self.stdout.write('1. View P&L at: http://127.0.0.1:8000/reports/profit-loss/')
        self.stdout.write('2. Modify amounts in admin: http://127.0.0.1:8000/admin/accounting/journalentry/')
