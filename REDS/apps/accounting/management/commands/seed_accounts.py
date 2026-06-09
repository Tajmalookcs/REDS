from django.core.management.base import BaseCommand
from apps.accounting.models import AccountHead


ACCOUNTS = [
    # ASSETS
    {'code': '1001', 'name': 'Cash in Hand',          'type': 'ASSET'},
    {'code': '1002', 'name': 'Petty Cash',             'type': 'ASSET'},
    {'code': '1003', 'name': 'Cheques in Hand',        'type': 'ASSET'},
    {'code': '1010', 'name': 'Bank Accounts',          'type': 'ASSET'},
    {'code': '1020', 'name': 'Land Asset',             'type': 'ASSET'},
    {'code': '1030', 'name': 'Plots Inventory',        'type': 'ASSET'},
    {'code': '1040', 'name': 'Customer Receivable',    'type': 'ASSET'},

    # LIABILITIES
    {'code': '2001', 'name': 'Landlord Payable',       'type': 'LIABILITY'},
    {'code': '2002', 'name': 'Refunds Payable',        'type': 'LIABILITY'},
    {'code': '2003', 'name': 'Agent Commission Payable','type': 'LIABILITY'},

    # EQUITY
    {'code': '3001', 'name': 'Owner Capital',          'type': 'EQUITY'},
    {'code': '3002', 'name': 'Retained Earnings',      'type': 'EQUITY'},

    # INCOME
    {'code': '4001', 'name': 'Plot Sales Revenue',     'type': 'INCOME'},
    {'code': '4002', 'name': 'Other Income',           'type': 'INCOME'},

    # EXPENSES
    {'code': '5001', 'name': 'Land Purchase Cost',     'type': 'EXPENSE'},
    {'code': '5002', 'name': 'Development Expenses',   'type': 'EXPENSE'},
    {'code': '5003', 'name': 'Agent Commission Expense','type': 'EXPENSE'},
    {'code': '5004', 'name': 'Staff Salaries',         'type': 'EXPENSE'},
    {'code': '5005', 'name': 'Petty Cash Expenses',    'type': 'EXPENSE'},
    {'code': '5006', 'name': 'Utility Bills',          'type': 'EXPENSE'},
    {'code': '5007', 'name': 'Miscellaneous Expenses', 'type': 'EXPENSE'},
]


class Command(BaseCommand):
    help = 'Seed default Chart of Accounts'

    def handle(self, *args, **kwargs):
        created = 0
        skipped = 0
        for acc in ACCOUNTS:
            obj, was_created = AccountHead.objects.get_or_create(
                code=acc['code'],
                defaults={
                    'name':      acc['name'],
                    'type':      acc['type'],
                    'is_active': True,
                }
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {acc['code']} — {acc['name']}"))
            else:
                skipped += 1
                self.stdout.write(f"  Skipped (exists): {acc['code']} — {acc['name']}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Created: {created} | Skipped: {skipped}"
        ))