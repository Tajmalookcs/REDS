from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Expense, ExpenseCategory
from apps.development.models import Town


@login_required
def expense_list(request):
    category_id = request.GET.get('category')
    town_id     = request.GET.get('town')
    date_from   = request.GET.get('date_from', '').strip()
    date_to     = request.GET.get('date_to', '').strip()
    expenses    = Expense.objects.filter(
                    is_deleted=False
                  ).select_related('category', 'town').order_by('-expense_date')
    categories  = ExpenseCategory.objects.all()
    towns       = Town.objects.filter(is_deleted=False).order_by('name')

    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if town_id:
        expenses = expenses.filter(town_id=town_id)
    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)
    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)

    from django.db.models import Sum
    total = expenses.aggregate(t=Sum('amount'))['t'] or 0

    # Group by town
    groups = {}
    for e in expenses:
        key = e.town.name if e.town else '— No Town —'
        if key not in groups:
            groups[key] = {'expenses': [], 'subtotal': 0}
        groups[key]['expenses'].append(e)
        groups[key]['subtotal'] += e.amount

    return render(request, 'expenses/expense_list.html', {
        'expenses':          expenses,
        'groups':            groups,
        'categories':        categories,
        'towns':             towns,
        'selected_category': category_id,
        'selected_town':     town_id,
        'date_from':         date_from,
        'date_to':           date_to,
        'total':             total,
    })


@login_required
def expense_add(request):
    categories = ExpenseCategory.objects.all()
    towns      = Town.objects.filter(is_deleted=False).order_by('name')

    if request.method == 'POST':
        try:
            town_pk     = request.POST.get('town', '').strip()
            category_pk = request.POST.get('category', '').strip()
            Expense.objects.create(
                category     = ExpenseCategory.objects.filter(pk=category_pk).first() if category_pk else None,
                town         = Town.objects.filter(pk=town_pk).first() if town_pk else None,
                title        = request.POST.get('title'),
                amount       = request.POST.get('amount'),
                expense_date = request.POST.get('expense_date'),
                payment_mode = request.POST.get('payment_mode', 'CASH'),
                paid_to      = request.POST.get('paid_to', ''),
                cheque_no    = request.POST.get('cheque_no', ''),
                cheque_bank  = request.POST.get('cheque_bank', ''),
                cheque_date  = request.POST.get('cheque_date') or None,
                narration    = request.POST.get('narration', ''),
                image        = request.FILES.get('image'),
                created_by   = request.user,
            )
            messages.success(request, 'Expense recorded.')
            return redirect('expenses:expense_list')
        except Exception as e:
            messages.error(request, f'Could not save expense: {e}')

    from django.utils import timezone
    return render(request, 'expenses/expense_form.html', {
        'categories': categories,
        'towns':      towns,
        'title':      'Add Expense',
        'today':      timezone.now().date(),
    })


@login_required
def expense_edit(request, pk):
    expense    = get_object_or_404(Expense, pk=pk, is_deleted=False)
    categories = ExpenseCategory.objects.all()
    towns      = Town.objects.filter(is_deleted=False).order_by('name')

    if request.method == 'POST':
        town_pk = request.POST.get('town')
        expense.category     = ExpenseCategory.objects.filter(
                                   pk=request.POST.get('category')
                               ).first()
        expense.town         = Town.objects.filter(pk=town_pk).first() if town_pk else None
        expense.title        = request.POST.get('title')
        expense.amount       = request.POST.get('amount')
        expense.expense_date = request.POST.get('expense_date')
        expense.payment_mode = request.POST.get('payment_mode', 'CASH')
        expense.paid_to      = request.POST.get('paid_to', '')
        expense.cheque_no    = request.POST.get('cheque_no', '')
        expense.cheque_bank  = request.POST.get('cheque_bank', '')
        expense.cheque_date  = request.POST.get('cheque_date') or None
        expense.narration    = request.POST.get('narration', '')
        if request.FILES.get('image'):
            expense.image = request.FILES.get('image')
        expense.save()
        messages.success(request, 'Expense updated.')
        return redirect('expenses:expense_list')

    return render(request, 'expenses/expense_form.html', {
        'expense':    expense,
        'categories': categories,
        'towns':      towns,
        'title':      'Edit Expense',
        'today':      timezone.localdate().isoformat(),
    })

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, is_deleted=False)
    expense.is_deleted = True
    expense.save()
    messages.success(request, 'Expense deleted.')
    return redirect('expenses:expense_list')


@login_required
def expense_print(request):
    from django.db.models import Sum
    from apps.core.models import BusinessProfile
    category_id = request.GET.get('category')
    town_id     = request.GET.get('town')
    date_from   = request.GET.get('date_from', '').strip()
    date_to     = request.GET.get('date_to', '').strip()
    expenses    = Expense.objects.filter(
                    is_deleted=False
                  ).select_related('category', 'town').order_by('town__name', '-expense_date')
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if town_id:
        expenses = expenses.filter(town_id=town_id)
    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)
    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)

    total = expenses.aggregate(t=Sum('amount'))['t'] or 0
    groups = {}
    for e in expenses:
        key = e.town.name if e.town else '— No Town —'
        if key not in groups:
            groups[key] = {'expenses': [], 'subtotal': 0}
        groups[key]['expenses'].append(e)
        groups[key]['subtotal'] += e.amount

    business = BusinessProfile.objects.first()
    return render(request, 'expenses/expense_print.html', {
        'groups':   groups,
        'total':    total,
        'business': business,
    })


@login_required
def category_list(request):
    categories = ExpenseCategory.objects.all()
    return render(request, 'expenses/category_list.html', {
        'categories': categories
    })


@login_required
def category_add(request):
    if request.method == 'POST':
        ExpenseCategory.objects.create(
            name        = request.POST.get('name'),
            description = request.POST.get('description', ''),
        )
        messages.success(request, 'Category added.')
        return redirect('expenses:category_list')
    return render(request, 'expenses/category_form.html', {'title': 'Add Category'})


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(ExpenseCategory, pk=pk)
    cat.delete()
    messages.success(request, 'Category deleted.')
    return redirect('expenses:category_list')