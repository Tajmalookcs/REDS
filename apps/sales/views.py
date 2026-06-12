from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from requests import request
from .models import Booking, PaymentPlan, Receipt, Cancellation, AgentCommission, RefundReceipt
from apps.development.models import Plot
from apps.customers.models import Customer
from apps.agents.models import Agent
from apps.sales.models import PlotTransfer


# ======================================================
# UTILITY — Auto Receipt Number
# ======================================================

def generate_receipt_no():
    last = Receipt.objects.order_by('-id').first()
    if last:
        try:
            num = int(last.receipt_no.split('-')[-1]) + 1
        except Exception:
            num = 1
    else:
        num = 1
    return f"RCP-{num:05d}"


def generate_refund_receipt_no():
    last = RefundReceipt.objects.order_by('-id').first()
    if last:
        try:
            num = int(last.receipt_no.split('-')[-1]) + 1
        except Exception:
            num = 1
    else:
        num = 1
    return f"RFD-{num:05d}"


# ======================================================
# BOOKING LIST
# ======================================================

@login_required
def booking_list(request):
    status   = request.GET.get('status', 'ACTIVE')
    bookings = Booking.objects.filter(
                    is_deleted=False
               ).select_related(
                    'customer', 'plot__block__town', 'agent'
               ).order_by('-created_at')

    if status:
        bookings = bookings.filter(status=status)

    return render(request, 'sales/booking_list.html', {
        'bookings':        bookings,
        'selected_status': status,
        'status_choices':  Booking.STATUS_CHOICES,
    })

# ======================================================
# BOOKING ADD
# ======================================================

@login_required
@transaction.atomic
def booking_add(request):
    plots     = Plot.objects.filter(
                    status='AVAILABLE',
                    is_deleted=False
                ).select_related('block__town').order_by('block__town__name', 'plot_no')
    customers         = Customer.objects.filter(is_deleted=False).order_by('name')
    agents            = Agent.objects.filter(is_deleted=False).order_by('name')
    selected_customer = request.GET.get('customer', '')

    if request.method == 'POST':
        plot     = get_object_or_404(Plot, pk=request.POST.get('plot'))
        agent_pk = request.POST.get('agent')
        agent    = Agent.objects.filter(pk=agent_pk).first() if agent_pk else None

        # ── Customer: existing or new inline ──────────
        customer_id = request.POST.get('customer')
        if customer_id:
            customer = get_object_or_404(Customer, pk=customer_id)
        else:
            new_name    = request.POST.get('new_name', '').strip()
            new_contact = request.POST.get('new_contact', '').strip()
            if not new_name or not new_contact:
                messages.error(request, 'Customer Name and Contact are required.')
                return redirect('sales:booking_add')
            customer = Customer.objects.create(
                name    = new_name,
                phone   = new_contact,
                cnic    = request.POST.get('new_cnic', '').strip(),
                address = request.POST.get('new_address', '').strip(),
                city    = request.POST.get('new_city', '').strip(),
            )

        total_price  = Decimal(request.POST.get('total_price', '0'))
        discount     = Decimal(request.POST.get('discount', '0'))
        net_price    = total_price - discount
        down_payment = Decimal(request.POST.get('down_payment', '0'))

        # Create Booking
        booking = Booking.objects.create(
            plot         = plot,
            customer     = customer,
            agent        = agent,
            booking_date = request.POST.get('booking_date'),
            total_price  = total_price,
            discount     = discount,
            net_price    = net_price,
            down_payment = down_payment,
            status       = 'ACTIVE',
            notes        = request.POST.get('notes', ''),
            created_by   = request.user,
        )

        # Update plot status to BOOKED
        plot.status = 'BOOKED'
        plot.save()

        # Auto-create agent commission if agent selected
        if agent:
            rate = Decimal(request.POST.get('commission_rate', '0'))
            if rate > 0:
                AgentCommission.objects.create(
                    booking           = booking,
                    agent             = agent,
                    commission_rate   = rate,
                    commission_amount = (net_price * rate) / 100,
                    created_by        = request.user,
                )

        # Auto receipt for down payment
        if down_payment > 0:
            Receipt.objects.create(
                booking      = booking,
                receipt_no   = generate_receipt_no(),
                receipt_date = request.POST.get('booking_date'),
                amount       = down_payment,
                payment_mode = request.POST.get('payment_mode', 'CASH'),
                narration    = 'Down Payment',
                created_by   = request.user,
            )

        # First installment (optional inline entry)
        inst_date   = request.POST.get('inst_date', '').strip()
        inst_amount = request.POST.get('inst_amount', '').strip()
        if inst_date and inst_amount:
            PaymentPlan.objects.create(
                booking        = booking,
                installment_no = 1,
                due_date       = inst_date,
                amount         = Decimal(inst_amount),
                created_at     = booking.created_at,
            )

        messages.success(request, f'Booking #{booking.pk} created successfully.')
        return redirect('sales:booking_detail', pk=booking.pk)

    return render(request, 'sales/booking_form.html', {
        'plots':             plots,
        'customers':         customers,
        'agents':            agents,
        'title':             'New Booking',
        'selected_customer': selected_customer,
    })


# ======================================================
# BOOKING DETAIL
# ======================================================

@login_required
def booking_detail(request, pk):
    booking       = get_object_or_404(Booking, pk=pk, is_deleted=False)
    payment_plans = booking.payment_plans.all()
    receipts      = booking.receipts.filter(is_deleted=False).order_by('-receipt_date')
    today         = timezone.now().date()
    cancellation  = Cancellation.objects.filter(booking=booking).first()

    return render(request, 'sales/booking_detail.html', {
        'booking':       booking,
        'payment_plans': payment_plans,
        'receipts':      receipts,
        'today':         today,
        'cancellation':  cancellation,
    })


# ======================================================
# BOOKING EDIT
# ======================================================

@login_required
def booking_edit(request, pk):
    booking   = get_object_or_404(Booking, pk=pk, is_deleted=False)
    customers = Customer.objects.filter(is_deleted=False).order_by('name')
    agents    = Agent.objects.filter(is_deleted=False).order_by('name')

    if request.method == 'POST':
        booking.notes  = request.POST.get('notes', '')
        booking.status = request.POST.get('status', booking.status)
        agent_pk       = request.POST.get('agent', '').strip()
        booking.agent  = Agent.objects.filter(pk=agent_pk).first() if agent_pk else None
        booking.save()
        messages.success(request, 'Booking updated.')
        return redirect('sales:booking_detail', pk=booking.pk)

    return render(request, 'sales/booking_edit.html', {
        'booking': booking,
        'agents':  agents,
        'title':   'Edit Booking',
    })


# ======================================================
# BOOKING DELETE (soft)
# ======================================================

@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, is_deleted=False)

    if booking.total_paid > 0:
        messages.error(request, 'Cannot delete a booking that has receipts.')
        return redirect('sales:booking_list')

    booking.plot.status = 'AVAILABLE'
    booking.plot.save()

    booking.is_deleted = True
    booking.save()
    messages.success(request, 'Booking deleted.')
    return redirect('sales:booking_list')


# ======================================================
# PAYMENT PLAN — ADD INSTALLMENTS
# ======================================================

@login_required
def plan_add(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, is_deleted=False)

    if request.method == 'POST':
        PaymentPlan.objects.create(
            booking        = booking,
            installment_no = request.POST.get('installment_no'),
            due_date       = request.POST.get('due_date'),
            amount         = Decimal(request.POST.get('amount', '0')),
            notes          = request.POST.get('notes', ''),
        )
        # Return JSON if AJAX/fetch, redirect if normal form
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or \
           not request.POST.get('_redirect', True):
            from django.http import JsonResponse
            return JsonResponse({'success': True})
        messages.success(request, 'Installment added.')
        return redirect('sales:booking_detail', pk=booking_pk)

    return redirect('sales:booking_detail', pk=booking_pk)

# ======================================================
# RECEIPT — ADD
# ======================================================

@login_required
def receipt_add(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, is_deleted=False)

    if request.method == 'POST':
        plan_pk = request.POST.get('payment_plan')
        plan    = PaymentPlan.objects.filter(pk=plan_pk).first() if plan_pk else None
        amount  = Decimal(request.POST.get('amount', '0'))

        receipt = Receipt.objects.create(
            booking      = booking,
            payment_plan = plan,
            receipt_no   = generate_receipt_no(),
            receipt_date = request.POST.get('receipt_date'),
            amount       = amount,
            payment_mode = request.POST.get('payment_mode', 'CASH'),
            cheque_no    = request.POST.get('cheque_no', ''),
            cheque_bank  = request.POST.get('cheque_bank', ''),
            cheque_date  = request.POST.get('cheque_date') or None,
            narration    = request.POST.get('narration', ''),
            created_by   = request.user,
        )

        # Update payment plan status if linked
        if plan:
            plan.paid_amount = (plan.paid_amount or Decimal('0')) + amount
            plan.paid_date   = request.POST.get('receipt_date')
            if plan.paid_amount >= plan.amount:
                plan.status = 'PAID'
            else:
                plan.status = 'PARTIAL'
            plan.save()

        # Mark booking COMPLETED if fully paid
        if booking.balance <= 0:
            booking.status      = 'COMPLETED'
            booking.plot.status = 'SOLD'
            booking.plot.save()
            booking.save()

        messages.success(request, f'Receipt {receipt.receipt_no} recorded.')
        return redirect('sales:booking_detail', pk=booking_pk)

    return redirect('sales:booking_detail', pk=booking_pk)


# ======================================================
# RECEIPT LIST
# ======================================================

@login_required
def receipt_list(request):
    receipts = Receipt.objects.filter(
                    is_deleted=False
               ).select_related(
                    'booking__customer', 'booking__plot'
               ).order_by('-receipt_date')

    return render(request, 'sales/receipt_list.html', {
        'receipts': receipts,
    })


# ======================================================
# CANCELLATION
# ======================================================

@login_required
@transaction.atomic
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, is_deleted=False)

    if hasattr(booking, 'cancellation'):
        messages.error(request, 'This booking is already cancelled.')
        return redirect('sales:booking_detail', pk=pk)

    if request.method == 'POST':
        Cancellation.objects.create(
            booking           = booking,
            cancellation_date = request.POST.get('cancellation_date'),
            reason            = request.POST.get('reason', ''),
            refund_amount     = Decimal(request.POST.get('refund_amount', '0')),
            deduction_amount  = Decimal(request.POST.get('deduction_amount', '0')),
            notes             = request.POST.get('notes', ''),
            created_by        = request.user,
        )

        booking.status      = 'CANCELLED'
        booking.plot.status = 'AVAILABLE'
        booking.plot.save()
        booking.save()

        messages.success(request, 'Booking cancelled successfully.')
        return redirect('sales:booking_list')

    return render(request, 'sales/booking_cancel.html', {
        'booking': booking,
        'today':   timezone.now().date(),
    })


# ======================================================
# RECEIPT PRINT
# ======================================================

@login_required
def receipt_print(request, pk):
    from apps.core.models import BusinessProfile
    receipt  = get_object_or_404(Receipt, pk=pk)
    business = BusinessProfile.objects.first()
    return render(request, 'sales/receipt_print.html', {
        'receipt':  receipt,
        'business': business,
    })


# ======================================================
# BOOKING PRINT
# ======================================================

@login_required
def booking_print(request, pk):
    from apps.core.models import BusinessProfile
    booking      = get_object_or_404(Booking, pk=pk)
    business     = BusinessProfile.objects.first()
    installments = PaymentPlan.objects.filter(booking=booking).order_by('installment_no')
    receipts_qs  = Receipt.objects.filter(booking=booking, is_deleted=False).order_by('receipt_date', 'id')
    total_paid   = receipts_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    balance      = booking.net_price - total_paid

    # Build receipts with running balance
    running = booking.net_price
    receipts_with_balance = []
    for r in receipts_qs:
        running = running - r.amount
        receipts_with_balance.append({
            'receipt_no':      r.receipt_no,
            'receipt_date':    r.receipt_date,
            'amount':          r.amount,
            'running_balance': running,
        })

    # Decompose plot size into marlas + sqft for display
    plot          = booking.plot
    size_marlas   = float(plot.size or 0)
    if plot.size_unit == 'KANAL':
        size_marlas *= 20
    elif plot.size_unit == 'SQFT':
        size_marlas /= 270
    plot_marla = int(size_marlas)
    plot_sqft  = round((size_marlas - plot_marla) * 270)

    return render(request, 'sales/booking_print.html', {
        'booking':      booking,
        'business':     business,
        'installments': installments,
        'receipts':     receipts_with_balance,
        'total_paid':   total_paid,
        'balance':      balance,
        'plot_marla':   plot_marla,
        'plot_sqft':    plot_sqft,
    })

# ======================================================
# PLOT TRANSFER
# ======================================================

@login_required
def transfer_create(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, is_deleted=False)

    total_paid        = booking.receipts.filter(is_deleted=False).aggregate(
                            t=Sum('amount'))['t'] or Decimal('0')
    remaining_balance = booking.net_price - total_paid

    if request.method == 'POST':
        transfer_type = request.POST.get('transfer_type')
        notes         = request.POST.get('notes', '')
        to_customer   = None

        if transfer_type == 'SELF':
            to_customer = booking.customer

        elif transfer_type == 'NEW_PERSON':
            name    = request.POST.get('new_name', '').strip()
            contact = request.POST.get('new_contact', '').strip()
            cnic    = request.POST.get('new_cnic', '').strip()
            address = request.POST.get('new_address', '').strip()

            if not name or not contact:
                messages.error(request, 'Name and Contact are required for new person.')
                return redirect('transfer_create', booking_id=booking_id)

            to_customer = Customer.objects.create(
                name    = name,
                phone   = contact,
                cnic    = cnic,
                address = address,
            )

        if to_customer:
            PlotTransfer.objects.create(
                booking           = booking,
                transfer_type     = transfer_type,
                from_customer     = booking.customer,
                to_customer       = to_customer,
                transfer_date     = timezone.now().date(),
                remaining_balance = remaining_balance,
                notes             = notes,
                status            = 'COMPLETED',
                created_by        = request.user,
            )

            if transfer_type == 'NEW_PERSON':
                booking.customer = to_customer
                booking.save()

            if remaining_balance <= 0:
                plot        = booking.plot
                plot.status = 'REGISTERED'
                plot.save()

            messages.success(request, 'Transfer completed successfully.')
            return redirect('sales:booking_detail', pk=booking_id)

    return render(request, 'sales/transfer_form.html', {
        'booking':           booking,
        'remaining_balance': remaining_balance,
    })

@login_required
def refund_pay(request, pk):
    cancellation = get_object_or_404(Cancellation, pk=pk)

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('refund_paid', '0'))
        except Exception:
            amount = Decimal('0')

        paid_date    = request.POST.get('refund_paid_date')
        payment_mode = request.POST.get('refund_payment_mode', 'CASH')
        notes        = request.POST.get('refund_notes', '')
        bank_account = request.POST.get('bank_account', '')
        cheque_no    = request.POST.get('cheque_no', '')
        cheque_bank  = request.POST.get('cheque_bank', '')
        cheque_date  = request.POST.get('cheque_date') or None

        if payment_mode not in {'CASH', 'BANK_TRANSFER', 'CHEQUE'}:
            payment_mode = 'CASH'

        if amount <= 0:
            messages.error(request, 'Refund amount must be greater than zero.')
            return redirect('sales:booking_detail', pk=cancellation.booking.pk)

        if amount > cancellation.refund_amount:
            messages.error(request, f'Refund amount cannot exceed Rs. {cancellation.refund_amount}.')
            return redirect('sales:booking_detail', pk=cancellation.booking.pk)

        if not paid_date:
            messages.error(request, 'Payment date is required.')
            return redirect('sales:booking_detail', pk=cancellation.booking.pk)

        with transaction.atomic():
            cancellation.refund_paid         = amount
            cancellation.refund_paid_date    = paid_date
            cancellation.refund_payment_mode = payment_mode
            cancellation.refund_notes        = notes
            cancellation.save()

            refund_receipt = RefundReceipt.objects.create(
                cancellation = cancellation,
                receipt_no   = generate_refund_receipt_no(),
                receipt_date = paid_date,
                amount       = amount,
                payment_mode = payment_mode,
                cheque_no    = cheque_no,
                cheque_bank  = cheque_bank,
                cheque_date  = cheque_date,
                bank_account = bank_account,
                narration    = notes,
                created_by   = request.user,
            )

            from apps.accounting.journal_auto import journal_on_refund_payment
            journal_on_refund_payment(cancellation, bank_account=bank_account, user=request.user)

        messages.success(request, f'Refund of Rs. {amount} marked as paid. Receipt {refund_receipt.receipt_no} created.')
        return redirect('sales:booking_detail', pk=cancellation.booking.pk)

    return redirect('sales:booking_detail', pk=cancellation.booking.pk)


@login_required
def refund_receipt_print(request, pk):
    from apps.core.models import BusinessProfile
    refund_receipt = get_object_or_404(RefundReceipt, pk=pk)
    business = BusinessProfile.objects.first()
    return render(request, 'sales/refund_receipt_print.html', {
        'refund_receipt': refund_receipt,
        'business':       business,
    })


@login_required
def refund_list(request):
    status_filter = request.GET.get('status', 'all')
    cancellations = Cancellation.objects.select_related(
        'booking__customer', 'booking__plot__block__town'
    ).order_by('-cancellation_date')

    if status_filter == 'pending':
        cancellations = cancellations.filter(refund_amount__gt=0, refund_paid=0)
    elif status_filter == 'paid':
        cancellations = cancellations.filter(refund_paid__gt=0)

    return render(request, 'sales/refund_list.html', {
        'cancellations': cancellations,
        'status_filter':  status_filter,
    })
