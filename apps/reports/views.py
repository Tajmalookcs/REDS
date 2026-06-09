from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date

from apps.development.models import Plot, Town, Block
from apps.sales.models import Booking, Receipt, AgentCommission
from apps.customers.models import Customer
from apps.agents.models import Agent
from apps.expenses.models import Expense, ExpenseCategory


# ─────────────────────────────────────────
# 1. SALES SUMMARY REPORT
# ─────────────────────────────────────────
@login_required
def sales_summary(request):
    from datetime import date
    
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')

    if not date_from or not date_to:
        today = date.today()
        first_day = today.replace(day=1)
        if not date_from:
            date_from = str(first_day)
        if not date_to:
            date_to = str(today)

    bookings = Booking.objects.filter(is_deleted=False).select_related(
        'plot__block__town', 'customer', 'agent'
    )

    if date_from:
        bookings = bookings.filter(booking_date__gte=date_from)
    if date_to:
        bookings = bookings.filter(booking_date__lte=date_to)

    total_bookings    = bookings.count()
    active_bookings   = bookings.filter(status='ACTIVE').count()
    completed         = bookings.filter(status='COMPLETED').count()
    cancelled         = bookings.filter(status='CANCELLED').count()

    total_net_price   = bookings.aggregate(t=Sum('net_price'))['t'] or 0

    receipts = Receipt.objects.filter(
        booking__in=bookings
    ).aggregate(t=Sum('amount'))['t'] or 0

    context = {
        'bookings':         bookings.order_by('-booking_date'),
        'total_bookings':   total_bookings,
        'active_bookings':  active_bookings,
        'completed':        completed,
        'cancelled':        cancelled,
        'total_net_price':  total_net_price,
        'total_received':   receipts,
        'date_from':        date_from,
        'date_to':          date_to,
    }
    return render(request, 'reports/sales_summary.html', context)


# ─────────────────────────────────────────
# 2. PLOT AVAILABILITY REPORT
# ─────────────────────────────────────────
@login_required
def plot_availability(request):
    town_id  = request.GET.get('town', '')
    block_id = request.GET.get('block', '')
    status   = request.GET.get('status', '')

    plots = Plot.objects.filter(is_deleted=False).select_related('block__town')

    if town_id:
        plots = plots.filter(block__town__id=town_id)
    if block_id:
        plots = plots.filter(block__id=block_id)
    if status:
        plots = plots.filter(status=status)

    towns  = Town.objects.filter(is_deleted=False)
    blocks = Block.objects.filter(is_deleted=False)

    summary = {
        'AVAILABLE': plots.filter(status='AVAILABLE').count(),
        'BOOKED':    plots.filter(status='BOOKED').count(),
        'SOLD':      plots.filter(status='SOLD').count(),
        'HOLD':      plots.filter(status='HOLD').count(),
    }

    context = {
        'plots':        plots.order_by('block__town__name', 'block__name', 'plot_no'),
        'towns':        towns,
        'blocks':       blocks,
        'summary':      summary,
        'sel_town':     town_id,
        'sel_block':    block_id,
        'sel_status':   status,
    }
    return render(request, 'reports/plot_availability.html', context)


# ─────────────────────────────────────────
# 3. CUSTOMER LEDGER
# ─────────────────────────────────────────
@login_required
def customer_ledger(request):
    customer_id = request.GET.get('customer', '')
    customer    = None
    bookings    = []
    receipts    = []
    total_price = 0
    total_paid  = 0
    balance     = 0

    customers = Customer.objects.filter(is_deleted=False).order_by('name')

    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
        bookings = Booking.objects.filter(
            customer=customer,
            is_deleted=False
        ).select_related('plot__block__town')

        receipts = Receipt.objects.filter(
            booking__customer=customer
        ).select_related('booking').order_by('receipt_date')

        total_price = bookings.aggregate(t=Sum('net_price'))['t'] or 0
        total_paid  = receipts.aggregate(t=Sum('amount'))['t'] or 0
        balance     = total_price - total_paid

    context = {
        'customers':    customers,
        'customer':     customer,
        'bookings':     bookings,
        'receipts':     receipts,
        'total_price':  total_price,
        'total_paid':   total_paid,
        'balance':      balance,
        'sel_customer': customer_id,
    }
    return render(request, 'reports/customer_ledger.html', context)


# ─────────────────────────────────────────
# 4. AGENT COMMISSION REPORT
# ─────────────────────────────────────────
@login_required
def agent_commission(request):
    agent_id  = request.GET.get('agent', '')
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')

    agents      = Agent.objects.filter(is_deleted=False).order_by('name')
    commissions = AgentCommission.objects.select_related(
        'agent', 'booking__plot__block__town', 'booking__customer'
    )

    if agent_id:
        commissions = commissions.filter(agent__id=agent_id)
    if date_from:
        commissions = commissions.filter(booking__booking_date__gte=date_from)
    if date_to:
        commissions = commissions.filter(booking__booking_date__lte=date_to)

    total_commission = commissions.aggregate(t=Sum('commission_amount'))['t'] or 0
    total_paid       = commissions.filter(status='PAID').aggregate(t=Sum('commission_amount'))['t'] or 0
    total_pending    = commissions.filter(status='PENDING').aggregate(t=Sum('commission_amount'))['t'] or 0

    context = {
        'agents':            agents,
        'commissions':       commissions.order_by('-booking__booking_date'),
        'total_commission':  total_commission,
        'total_paid':        total_paid,
        'total_pending':     total_pending,
        'sel_agent':         agent_id,
        'date_from':         date_from,
        'date_to':           date_to,
    }
    return render(request, 'reports/agent_commission.html', context)


# ─────────────────────────────────────────
# 5. EXPENSE SUMMARY REPORT  ← FIXED
# ─────────────────────────────────────────
@login_required
def expense_summary(request):
    from datetime import date
    
    date_from   = request.GET.get('date_from', '')
    date_to     = request.GET.get('date_to', '')
    category_id = request.GET.get('category', '')

    if not date_from or not date_to:
        today = date.today()
        first_day = today.replace(day=1)
        if not date_from:
            date_from = str(first_day)
        if not date_to:
            date_to = str(today)

    expenses   = Expense.objects.select_related('category')
    categories = ExpenseCategory.objects.all()

    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)  # FIXED
    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)    # FIXED
    if category_id:
        expenses = expenses.filter(category__id=category_id)

    total_amount = expenses.aggregate(t=Sum('amount'))['t'] or 0

    by_category = expenses.values(
        'category__name'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')

    context = {
        'expenses':     expenses.order_by('-expense_date'),       # FIXED
        'categories':   categories,
        'by_category':  by_category,
        'total_amount': total_amount,
        'date_from':    date_from,
        'date_to':      date_to,
        'sel_category': category_id,
    }
    return render(request, 'reports/expense_summary.html', context)


# ─────────────────────────────────────────
# 6. LANDLORD PAYMENT REPORT
# ─────────────────────────────────────────
@login_required
def landlord_report(request):
    from apps.land.models import Landlord, LandContract, ContractPaymentSchedule

    landlord_id = request.GET.get('landlord', '')
    date_from   = request.GET.get('date_from', '')
    date_to     = request.GET.get('date_to', '')

    landlords = Landlord.objects.filter(is_deleted=False).order_by('name')
    schedules = ContractPaymentSchedule.objects.select_related(
        'contract__landlord'
    ).order_by('due_date')

    if landlord_id:
        schedules = schedules.filter(contract__landlord__id=landlord_id)
    if date_from:
        schedules = schedules.filter(due_date__gte=date_from)
    if date_to:
        schedules = schedules.filter(due_date__lte=date_to)

    total_amount  = schedules.aggregate(t=Sum('amount'))['t'] or 0
    total_paid    = schedules.filter(status='PAID').aggregate(t=Sum('paid_amount'))['t'] or 0
    total_pending = schedules.filter(status='PENDING').aggregate(t=Sum('amount'))['t'] or 0

    context = {
        'landlords':     landlords,
        'schedules':     schedules,
        'total_amount':  total_amount,
        'total_paid':    total_paid,
        'total_pending': total_pending,
        'sel_landlord':  landlord_id,
        'date_from':     date_from,
        'date_to':       date_to,
    }
    return render(request, 'reports/landlord_report.html', context)


# ─────────────────────────────────────────
# 7. CASH AND BANK POSITION REPORT
# ─────────────────────────────────────────
@login_required
def cash_bank_position(request):
    from apps.core.models import BankAccount
    from apps.accounting.models import AccountHead, JournalLine
    from apps.sales.models import Receipt
    from django.db.models import Sum

    cash_received = Receipt.objects.filter(
        is_deleted=False,
        payment_mode='CASH'
    ).aggregate(t=Sum('amount'))['t'] or 0

    bank_received = Receipt.objects.filter(
        is_deleted=False,
        payment_mode='BANK'
    ).aggregate(t=Sum('amount'))['t'] or 0

    cheques_received = Receipt.objects.filter(
        is_deleted=False,
        payment_mode='CHEQUE'
    ).aggregate(t=Sum('amount'))['t'] or 0

    try:
        cash_account = AccountHead.objects.get(code='1001')
        cash_dr = cash_account.lines.aggregate(t=Sum('debit'))['t'] or 0
        cash_cr = cash_account.lines.aggregate(t=Sum('credit'))['t'] or 0
        cash_balance = cash_dr - cash_cr
    except AccountHead.DoesNotExist:
        cash_balance = 0

    try:
        petty_account = AccountHead.objects.get(code='1002')
        petty_dr = petty_account.lines.aggregate(t=Sum('debit'))['t'] or 0
        petty_cr = petty_account.lines.aggregate(t=Sum('credit'))['t'] or 0
        petty_balance = petty_dr - petty_cr
    except AccountHead.DoesNotExist:
        petty_balance = 0

    try:
        cheque_account = AccountHead.objects.get(code='1003')
        cheque_dr = cheque_account.lines.aggregate(t=Sum('debit'))['t'] or 0
        cheque_cr = cheque_account.lines.aggregate(t=Sum('credit'))['t'] or 0
        cheque_balance = cheque_dr - cheque_cr
    except AccountHead.DoesNotExist:
        cheque_balance = 0

    banks = BankAccount.objects.filter(is_active=True)
    bank_opening_balance = sum([b.opening_balance for b in banks])

    if cash_balance == 0 and petty_balance == 0:
        total_cash    = cash_received
        total_cheques = cheques_received
        total_bank    = bank_opening_balance + bank_received
    else:
        total_cash    = (cash_balance + petty_balance) + cash_received
        total_cheques = cheque_balance + cheques_received
        total_bank    = bank_opening_balance + bank_received

    grand_total = total_cash + total_bank + total_cheques

    context = {
        'cash_balance':     cash_balance,
        'petty_balance':    petty_balance,
        'cheque_balance':   cheque_balance,
        'banks':            banks,
        'total_cash':       total_cash,
        'total_bank':       total_bank,
        'total_cheques':    total_cheques,
        'grand_total':      grand_total,
        'cash_received':    cash_received,
        'bank_received':    bank_received,
        'cheques_received': cheques_received,
    }
    return render(request, 'reports/cash_bank_position.html', context)


# ─────────────────────────────────────────
# 8. PROFIT AND LOSS STATEMENT
# ─────────────────────────────────────────
@login_required
def profit_loss(request):
    from apps.accounting.models import AccountHead
    from django.db.models import Sum
    from datetime import date

    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')

    if not date_from or not date_to:
        today = date.today()
        first_day = today.replace(day=1)
        if not date_from:
            date_from = str(first_day)
        if not date_to:
            date_to = str(today)

    def get_type_total(account_type, date_from='', date_to=''):
        accounts = AccountHead.objects.filter(type=account_type, is_active=True)
        rows = []
        total = 0
        for acc in accounts:
            lines = acc.lines.all()
            if date_from:
                lines = lines.filter(journal__entry_date__gte=date_from)
            if date_to:
                lines = lines.filter(journal__entry_date__lte=date_to)
            dr = lines.aggregate(t=Sum('debit'))['t'] or 0
            cr = lines.aggregate(t=Sum('credit'))['t'] or 0
            balance = cr - dr if account_type == 'INCOME' else dr - cr
            if balance != 0:
                rows.append({'account': acc, 'balance': balance})
                total += balance
        return rows, total

    income_rows,  total_income  = get_type_total('INCOME',  date_from, date_to)
    expense_rows, total_expense = get_type_total('EXPENSE', date_from, date_to)
    net_profit = total_income - total_expense

    context = {
        'income_rows':   income_rows,
        'expense_rows':  expense_rows,
        'total_income':  total_income,
        'total_expense': total_expense,
        'net_profit':    net_profit,
        'date_from':     date_from,
        'date_to':       date_to,
    }
    return render(request, 'reports/profit_loss.html', context)


# ─────────────────────────────────────────
# 9. INCOME TAX SUMMARY REPORT  ← FIXED
# ─────────────────────────────────────────
@login_required
def tax_summary(request):
    from apps.sales.models import Booking, Receipt
    from django.db.models import Sum
    from datetime import date

    tax_year  = request.GET.get('tax_year', '')
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')

    current_year = date.today().year
    year_choices = [str(y) for y in range(current_year, current_year - 6, -1)]

    bookings = Booking.objects.filter(
        is_deleted=False
    ).exclude(status='CANCELLED').select_related(
        'customer', 'plot__block__town', 'agent'
    )

    receipts = Receipt.objects.select_related('booking__customer')

    if date_from:
        bookings = bookings.filter(booking_date__gte=date_from)
        receipts = receipts.filter(receipt_date__gte=date_from)  # FIXED
    if date_to:
        bookings = bookings.filter(booking_date__lte=date_to)
        receipts = receipts.filter(receipt_date__lte=date_to)    # FIXED

    total_sale_value = bookings.aggregate(t=Sum('net_price'))['t'] or 0
    total_received   = receipts.aggregate(t=Sum('amount'))['t'] or 0
    total_bookings   = bookings.count()
    completed_sales  = bookings.filter(status='COMPLETED').count()

    from django.db.models import Count
    customer_summary = bookings.values(
        'customer__name',
        'customer__cnic',
    ).annotate(
        total_plots = Count('id'),
        total_value = Sum('net_price'),
    ).order_by('-total_value')

    context = {
        'bookings':         bookings.order_by('-booking_date'),
        'total_sale_value': total_sale_value,
        'total_received':   total_received,
        'total_bookings':   total_bookings,
        'completed_sales':  completed_sales,
        'customer_summary': customer_summary,
        'year_choices':     year_choices,
        'tax_year':         tax_year,
        'date_from':        date_from,
        'date_to':          date_to,
    }
    return render(request, 'reports/tax_summary.html', context)

# ─────────────────────────────────────────
# TOWN DETAIL REPORT
# ─────────────────────────────────────────
@login_required
def town_detail(request, town_pk):
    from apps.development.models import Town, Block, Plot, TownMap
    from apps.sales.models import Booking, Receipt
    from django.db.models import Sum

    town   = get_object_or_404(Town, pk=town_pk, is_deleted=False)
    blocks = Block.objects.filter(town=town, is_deleted=False)

    # All plots of this town
    town_plots = Plot.objects.filter(block__town=town, is_deleted=False)

    total_plots     = town_plots.count()
    sold_plots      = town_plots.filter(status='SOLD').count()
    booked_plots    = town_plots.filter(status='BOOKED').count()
    available_plots = town_plots.filter(status='AVAILABLE').count()
    hold_plots      = town_plots.filter(status='HOLD').count()

    # Financial
    # Total value of ALL plots
    total_plot_value = town_plots.aggregate(t=Sum('price'))['t'] or 0

    # Total value of sold/booked plots (from bookings)
    bookings = Booking.objects.filter(
        plot__block__town=town,
        is_deleted=False
    ).exclude(status='CANCELLED')

    total_booked_value   = bookings.aggregate(t=Sum('net_price'))['t'] or 0
    total_received       = Receipt.objects.filter(
                               booking__plot__block__town=town,
                               is_deleted=False
                           ).aggregate(t=Sum('amount'))['t'] or 0
    balance_receivable   = total_booked_value - total_received

    # Value of unsold plots
    unsold_plot_value = town_plots.filter(
        status__in=['AVAILABLE', 'HOLD']
    ).aggregate(t=Sum('price'))['t'] or 0

    # Per-block stats
    blocks_data = []
    for block in blocks:
        block_plots = Plot.objects.filter(block=block, is_deleted=False)
        blocks_data.append({
            'block':     block,
            'total':     block_plots.count(),
            'sold':      block_plots.filter(status='SOLD').count(),
            'booked':    block_plots.filter(status='BOOKED').count(),
            'available': block_plots.filter(status='AVAILABLE').count(),
            'hold':      block_plots.filter(status='HOLD').count(),
        })

    # Town images
    town_images = town.maps.filter(map_type='IMAGE', is_active=True)

    context = {
        'town':               town,
        'blocks_data':        blocks_data,
        'total_plots':        total_plots,
        'sold_plots':         sold_plots,
        'booked_plots':       booked_plots,
        'available_plots':    available_plots,
        'hold_plots':         hold_plots,
        'total_plot_value':   total_plot_value,
        'total_booked_value': total_booked_value,
        'total_received':     total_received,
        'balance_receivable': balance_receivable,
        'unsold_plot_value':  unsold_plot_value,
        'town_images':        town_images,
    }
    return render(request, 'reports/town_detail.html', context)