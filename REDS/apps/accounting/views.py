from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone

from apps.accounting.models import AccountHead, JournalEntry, JournalLine


# ─────────────────────────────────────────
# CHART OF ACCOUNTS
# ─────────────────────────────────────────
@login_required
def account_list(request):
    accounts = AccountHead.objects.all().order_by('code')
    return render(request, 'accounting/account_list.html', {'accounts': accounts})


@login_required
def account_add(request):
    if request.method == 'POST':
        AccountHead.objects.create(
            code        = request.POST['code'],
            name        = request.POST['name'],
            type        = request.POST['type'],
            description = request.POST.get('description', ''),
            is_active   = True,
        )
        return redirect('accounting:account_list')
    return render(request, 'accounting/account_form.html', {'title': 'Add Account'})


@login_required
def account_edit(request, pk):
    account = get_object_or_404(AccountHead, pk=pk)
    if request.method == 'POST':
        account.code        = request.POST['code']
        account.name        = request.POST['name']
        account.type        = request.POST['type']
        account.description = request.POST.get('description', '')
        account.is_active   = 'is_active' in request.POST
        account.save()
        return redirect('accounting:account_list')
    return render(request, 'accounting/account_form.html', {
        'title':   'Edit Account',
        'account': account,
    })


# ─────────────────────────────────────────
# JOURNAL ENTRIES
# ─────────────────────────────────────────
@login_required
def journal_list(request):
    journals = JournalEntry.objects.all().order_by('-entry_date', '-pk')
    return render(request, 'accounting/journal_list.html', {'journals': journals})


@login_required
def journal_add(request):
    accounts = AccountHead.objects.filter(is_active=True).order_by('code')
    if request.method == 'POST':
        entry = JournalEntry.objects.create(
            entry_date  = request.POST['entry_date'],
            reference   = request.POST.get('reference', ''),
            narration   = request.POST.get('narration', ''),
            created_by  = request.user,
        )
        account_ids = request.POST.getlist('account')
        debits      = request.POST.getlist('debit')
        credits     = request.POST.getlist('credit')
        narrations  = request.POST.getlist('line_narration')

        for i in range(len(account_ids)):
            if account_ids[i]:
                JournalLine.objects.create(
                    journal   = entry,
                    account_id= account_ids[i],
                    debit     = debits[i] or 0,
                    credit    = credits[i] or 0,
                    narration = narrations[i] if i < len(narrations) else '',
                )
        return redirect('accounting:journal_list')
    return render(request, 'accounting/journal_form.html', {
        'accounts': accounts,
        'title':    'New Journal Entry',
    })


@login_required
def journal_detail(request, pk):
    journal = get_object_or_404(JournalEntry, pk=pk)
    lines   = journal.lines.select_related('account').all()
    return render(request, 'accounting/journal_detail.html', {
        'journal': journal,
        'lines':   lines,
    })


# ─────────────────────────────────────────
# CASH BOOK
# ─────────────────────────────────────────
@login_required
def cash_book(request):
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')

    try:
        cash_account = AccountHead.objects.get(code='1001')
    except AccountHead.DoesNotExist:
        cash_account = None

    lines = JournalLine.objects.filter(
        account=cash_account
    ).select_related('journal').order_by('journal__entry_date', 'journal__pk')

    if date_from:
        lines = lines.filter(journal__entry_date__gte=date_from)
    if date_to:
        lines = lines.filter(journal__entry_date__lte=date_to)

    total_debit  = lines.aggregate(t=Sum('debit'))['t'] or 0
    total_credit = lines.aggregate(t=Sum('credit'))['t'] or 0
    balance      = total_debit - total_credit

    context = {
        'lines':        lines,
        'total_debit':  total_debit,
        'total_credit': total_credit,
        'balance':      balance,
        'date_from':    date_from,
        'date_to':      date_to,
        'account':      cash_account,
    }
    return render(request, 'accounting/cash_book.html', context)


# ─────────────────────────────────────────
# GENERAL LEDGER
# ─────────────────────────────────────────
@login_required
def general_ledger(request):
    account_id = request.GET.get('account', '')
    date_from  = request.GET.get('date_from', '')
    date_to    = request.GET.get('date_to', '')

    accounts = AccountHead.objects.filter(is_active=True).order_by('code')
    lines    = JournalLine.objects.none()
    account  = None
    total_debit  = 0
    total_credit = 0
    balance      = 0

    if account_id:
        account = get_object_or_404(AccountHead, pk=account_id)
        lines   = JournalLine.objects.filter(
            account=account
        ).select_related('journal').order_by('journal__entry_date', 'journal__pk')

        if date_from:
            lines = lines.filter(journal__entry_date__gte=date_from)
        if date_to:
            lines = lines.filter(journal__entry_date__lte=date_to)

        total_debit  = lines.aggregate(t=Sum('debit'))['t'] or 0
        total_credit = lines.aggregate(t=Sum('credit'))['t'] or 0
        balance      = total_debit - total_credit

    context = {
        'accounts':     accounts,
        'lines':        lines,
        'account':      account,
        'total_debit':  total_debit,
        'total_credit': total_credit,
        'balance':      balance,
        'date_from':    date_from,
        'date_to':      date_to,
        'sel_account':  account_id,
    }
    return render(request, 'accounting/general_ledger.html', context)


# ─────────────────────────────────────────
# TRIAL BALANCE
# ─────────────────────────────────────────
@login_required
def trial_balance(request):
    accounts = AccountHead.objects.filter(is_active=True).order_by('code')

    rows = []
    total_debit  = 0
    total_credit = 0

    for acc in accounts:
        dr = acc.lines.aggregate(t=Sum('debit'))['t'] or 0
        cr = acc.lines.aggregate(t=Sum('credit'))['t'] or 0
        net = dr - cr
        if dr > 0 or cr > 0:
            rows.append({
                'account':      acc,
                'total_debit':  dr,
                'total_credit': cr,
                'balance':      abs(net),
                'side':         'DR' if net >= 0 else 'CR',
            })
            if net >= 0:
                total_debit += abs(net)
            else:
                total_credit += abs(net)

    context = {
        'rows':         rows,
        'total_debit':  total_debit,
        'total_credit': total_credit,
    }
    return render(request, 'accounting/trial_balance.html', context)



# ─────────────────────────────────────────
# BANK LEDGER
# ─────────────────────────────────────────
@login_required
def bank_ledger(request):
    from apps.core.models import BankAccount
    from datetime import date, timedelta
    
    bank_id   = request.GET.get('bank', '')
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')

    # Set default dates: 1st of month to today
    if not date_from or not date_to:
        today = date.today()
        first_day = today.replace(day=1)
        if not date_from:
            date_from = str(first_day)
        if not date_to:
            date_to = str(today)

    banks    = BankAccount.objects.filter(is_active=True)
    lines    = JournalLine.objects.none()
    account  = None
    bank     = None
    total_debit  = 0
    total_credit = 0
    balance      = 0

    if bank_id:
        bank = get_object_or_404(BankAccount, pk=bank_id)
        try:
            account = AccountHead.objects.get(code='1010')
        except AccountHead.DoesNotExist:
            account = None

        lines = JournalLine.objects.filter(
            account=account
        ).select_related('journal').order_by('journal__entry_date', 'journal__pk')

        if date_from:
            lines = lines.filter(journal__entry_date__gte=date_from)
        if date_to:
            lines = lines.filter(journal__entry_date__lte=date_to)

        total_debit  = lines.aggregate(t=Sum('debit'))['t'] or 0
        total_credit = lines.aggregate(t=Sum('credit'))['t'] or 0
        balance      = total_debit - total_credit

    context = {
        'banks':        banks,
        'lines':        lines,
        'bank':         bank,
        'account':      account,
        'total_debit':  total_debit,
        'total_credit': total_credit,
        'balance':      balance,
        'date_from':    date_from,
        'date_to':      date_to,
        'sel_bank':     bank_id,
    }
    return render(request, 'accounting/bank_ledger.html', context)