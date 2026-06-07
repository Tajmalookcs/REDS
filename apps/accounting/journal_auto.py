from django.utils import timezone
from apps.accounting.models import AccountHead, JournalEntry, JournalLine


def get_account(code):
    try:
        return AccountHead.objects.get(code=code)
    except AccountHead.DoesNotExist:
        return None


def create_journal(narration, reference, lines, user=None):
    """
    lines = list of dicts:
    [
        {'account_code': '1001', 'debit': 5000, 'credit': 0},
        {'account_code': '1040', 'debit': 0,    'credit': 5000},
    ]
    """
    entry = JournalEntry.objects.create(
        entry_date  = timezone.now().date(),
        reference   = reference,
        narration   = narration,
        created_by  = user,
    )
    for line in lines:
        account = get_account(line['account_code'])
        if account:
            JournalLine.objects.create(
                journal  = entry,
                account  = account,
                debit    = line.get('debit', 0),
                credit   = line.get('credit', 0),
                narration= line.get('narration', ''),
            )
    return entry


# ─────────────────────────────────────────
# ON RECEIPT SAVED
# ─────────────────────────────────────────
def journal_on_receipt(receipt, user=None):
    amount    = receipt.amount
    ref       = receipt.receipt_no
    narration = f"Receipt {ref} — {receipt.booking.customer.name}"

    if receipt.payment_mode == 'CASH':
        lines = [
            {'account_code': '1001', 'debit': amount, 'credit': 0,      'narration': narration},
            {'account_code': '1040', 'debit': 0,      'credit': amount,  'narration': narration},
        ]
    elif receipt.payment_mode == 'BANK_TRANSFER':
        bank_code = str(receipt.bank_account.pk) if receipt.bank_account else '1010'
        lines = [
            {'account_code': bank_code, 'debit': amount, 'credit': 0,     'narration': narration},
            {'account_code': '1040',    'debit': 0,      'credit': amount, 'narration': narration},
        ]
    elif receipt.payment_mode == 'CHEQUE':
        lines = [
            {'account_code': '1003', 'debit': amount, 'credit': 0,      'narration': narration},
            {'account_code': '1040', 'debit': 0,      'credit': amount,  'narration': narration},
        ]
    else:
        return None

    return create_journal(narration, ref, lines, user)


# ─────────────────────────────────────────
# ON BOOKING CONFIRMED
# ─────────────────────────────────────────
def journal_on_booking(booking, user=None):
    amount    = booking.net_price
    ref       = booking.booking_no
    narration = f"Booking {ref} — {booking.customer.name} — {booking.plot.plot_no}"

    lines = [
        {'account_code': '1040', 'debit': amount, 'credit': 0,      'narration': narration},
        {'account_code': '4001', 'debit': 0,      'credit': amount,  'narration': narration},
    ]
    return create_journal(narration, ref, lines, user)


# ─────────────────────────────────────────
# ON BOOKING CANCELLED (REFUND)
# ─────────────────────────────────────────
def journal_on_cancellation(cancellation, user=None):
    amount    = cancellation.refund_amount
    ref       = f"CANCEL-{cancellation.booking.booking_no}"
    narration = f"Cancellation {ref} — refund to {cancellation.booking.customer.name}"

    lines = [
        {'account_code': '4001', 'debit': amount, 'credit': 0,      'narration': narration},
        {'account_code': '2002', 'debit': 0,      'credit': amount,  'narration': narration},
    ]
    return create_journal(narration, ref, lines, user)


# ─────────────────────────────────────────
# ON LANDLORD PAYMENT
# ─────────────────────────────────────────
def journal_on_landlord_payment(schedule, user=None):
    amount    = schedule.paid_amount
    ref       = f"LAND-{schedule.contract.pk}-INS{schedule.installment_no}"
    narration = f"Landlord payment — {schedule.contract.landlord.name} — Installment {schedule.installment_no}"

    if schedule.payment_mode == 'CASH':
        lines = [
            {'account_code': '2001', 'debit': amount, 'credit': 0,      'narration': narration},
            {'account_code': '1001', 'debit': 0,      'credit': amount,  'narration': narration},
        ]
    elif schedule.payment_mode == 'BANK':
        bank_code = str(schedule.bank_account.pk) if schedule.bank_account else '1010'
        lines = [
            {'account_code': '2001',    'debit': amount, 'credit': 0,     'narration': narration},
            {'account_code': bank_code, 'debit': 0,      'credit': amount, 'narration': narration},
        ]
    else:
        return None

    return create_journal(narration, ref, lines, user)


# ─────────────────────────────────────────
# ON MISC EXPENSE SAVED
# ─────────────────────────────────────────
def journal_on_expense(expense, user=None):
    amount    = expense.amount
    ref       = expense.expense_no
    narration = f"Expense {ref} — {expense.description}"

    expense_account_code = '5007'  # Default: Miscellaneous Expenses

    if expense.payment_mode == 'PETTY_CASH':
        credit_code = '1002'
    elif expense.payment_mode == 'CASH':
        credit_code = '1001'
    elif expense.payment_mode == 'BANK':
        credit_code = str(expense.bank_account.pk) if expense.bank_account else '1010'
    else:
        credit_code = '1001'

    lines = [
        {'account_code': expense_account_code, 'debit': amount, 'credit': 0,      'narration': narration},
        {'account_code': credit_code,           'debit': 0,      'credit': amount,  'narration': narration},
    ]
    return create_journal(narration, ref, lines, user)


# ─────────────────────────────────────────
# ON AGENT COMMISSION PAID
# ─────────────────────────────────────────
def journal_on_commission_paid(commission, user=None):
    amount    = commission.commission_amount
    ref       = f"COMM-{commission.booking.booking_no}"
    narration = f"Commission paid — {commission.agent.name} — {commission.booking.booking_no}"

    if commission.paid_mode == 'CASH':
        credit_code = '1001'
    elif commission.paid_mode == 'BANK':
        credit_code = str(commission.bank_account.pk) if commission.bank_account else '1010'
    else:
        credit_code = '1001'

    lines = [
        {'account_code': '5003',      'debit': amount, 'credit': 0,      'narration': narration},
        {'account_code': credit_code, 'debit': 0,      'credit': amount,  'narration': narration},
    ]
    return create_journal(narration, ref, lines, user)