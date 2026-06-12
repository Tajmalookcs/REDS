from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Landlord, LandContract, ContractPaymentSchedule
from .forms import LandlordForm, LandContractForm, PaymentScheduleForm
from apps.core.models import BankAccount


# ======================================================
# LANDLORDS
# ======================================================

@login_required
def landlord_list(request):
    landlords = Landlord.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'land/landlord_list.html', {'landlords': landlords})


@login_required
def landlord_add(request):
    form = LandlordForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.save()
        messages.success(request, 'Landlord added successfully.')
        return redirect('land:landlord_list')
    return render(request, 'land/landlord_form.html', {
        'form': form, 'title': 'Add Landlord'
    })


@login_required
def landlord_edit(request, pk):
    landlord = get_object_or_404(Landlord, pk=pk, is_deleted=False)
    form = LandlordForm(request.POST or None, instance=landlord)
    if form.is_valid():
        form.save()
        messages.success(request, 'Landlord updated.')
        return redirect('land:landlord_list')
    return render(request, 'land/landlord_form.html', {
        'form': form, 'title': 'Edit Landlord'
    })


@login_required
def landlord_delete(request, pk):
    landlord = get_object_or_404(Landlord, pk=pk)
    landlord.is_deleted = True
    landlord.save()
    messages.success(request, 'Landlord deleted.')
    return redirect('land:landlord_list')


# ======================================================
# LAND CONTRACTS
# ======================================================

@login_required
def contract_list(request):
    contracts = LandContract.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'land/contract_list.html', {'contracts': contracts})


@login_required
def contract_add(request):
    landlords = Landlord.objects.filter(is_deleted=False).order_by('name')

    if request.method == 'POST':
        landlord = get_object_or_404(Landlord, pk=request.POST.get('landlord'))
        contract = LandContract.objects.create(
            landlord      = landlord,
            title         = request.POST.get('title'),
            total_area    = request.POST.get('total_area'),
            area_unit     = request.POST.get('area_unit', 'MARLA'),
            total_amount  = request.POST.get('total_amount'),
            contract_type = request.POST.get('contract_type', 'CASH'),
            start_date    = request.POST.get('start_date'),
            duration_years= request.POST.get('duration_years', 0),
            status        = request.POST.get('status', 'ACTIVE'),
            location      = request.POST.get('location', ''),
            notes         = request.POST.get('notes', ''),
            created_by    = request.user,
        )
        if request.FILES.get('contract_pdf'):
            contract.contract_pdf = request.FILES['contract_pdf']
            contract.save()
        messages.success(request, 'Land contract added.')
        return redirect('land:contract_list')

    return render(request, 'land/contract_form.html', {
        'landlords': landlords,
        'title':     'Add Land Contract',
    })


@login_required
def contract_edit(request, pk):
    contract  = get_object_or_404(LandContract, pk=pk, is_deleted=False)
    landlords = Landlord.objects.filter(is_deleted=False).order_by('name')

    if request.method == 'POST':
        contract.landlord       = get_object_or_404(Landlord, pk=request.POST.get('landlord'))
        contract.title          = request.POST.get('title')
        contract.total_area     = request.POST.get('total_area')
        contract.area_unit      = request.POST.get('area_unit', 'MARLA')
        contract.total_amount   = request.POST.get('total_amount')
        contract.contract_type  = request.POST.get('contract_type', 'CASH')
        contract.start_date     = request.POST.get('start_date')
        contract.duration_years = request.POST.get('duration_years', 0)
        contract.status         = request.POST.get('status', 'ACTIVE')
        contract.location       = request.POST.get('location', '')
        contract.notes          = request.POST.get('notes', '')
        if request.FILES.get('contract_pdf'):
            contract.contract_pdf = request.FILES['contract_pdf']
        contract.save()
        messages.success(request, 'Contract updated.')
        return redirect('land:contract_list')

    return render(request, 'land/contract_form.html', {
        'contract':  contract,
        'landlords': landlords,
        'title':     'Edit Land Contract',
    })


@login_required
def contract_delete(request, pk):
    contract = get_object_or_404(LandContract, pk=pk)
    contract.is_deleted = True
    contract.save()
    messages.success(request, 'Contract deleted.')
    return redirect('land:contract_list')


# ======================================================
# PAYMENT SCHEDULE
# ======================================================

@login_required
def payment_schedule(request, contract_pk):
    contract  = get_object_or_404(LandContract, pk=contract_pk)
    schedules = contract.schedules.all().order_by('installment_no')

    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        schedule    = get_object_or_404(ContractPaymentSchedule, pk=schedule_id)
        form = PaymentScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            if obj.paid_amount >= obj.amount:
                obj.status = 'PAID'
            elif obj.paid_amount > 0:
                obj.status = 'PARTIAL'
            obj.save()
            messages.success(request, 'Payment updated.')
            return redirect('land:payment_schedule', contract_pk=contract_pk)
    else:
        form = PaymentScheduleForm()

    return render(request, 'land/payment_schedule.html', {
        'contract':  contract,
        'schedules': schedules,
        'form':      form,
    })


@login_required
def schedule_add(request, contract_pk):
    contract = get_object_or_404(LandContract, pk=contract_pk)
    if request.method == 'POST':
        ContractPaymentSchedule.objects.create(
            contract       = contract,
            installment_no = request.POST.get('installment_no'),
            amount         = request.POST.get('amount'),
            due_date       = request.POST.get('due_date'),
            created_by     = request.user,
        )
        messages.success(request, 'Installment added.')
    return redirect('land:payment_schedule', contract_pk=contract_pk)