from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expense, ExpenseCategory
from apps.development.models import Town


@login_required
def expense_list(request):
    category_id = request.GET.get('category')
    town_id     = request.GET.get('town')
    expenses    = Expense.objects.filter(
                    is_deleted=False
                  ).select_related('category', 'town').order_by('-expense_date')
    categories  = ExpenseCategory.objects.all()
    towns       = Town.objects.filter(is_deleted=False).order_by('name')

    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if town_id:
        expenses = expenses.filter(town_id=town_id)

    return render(request, 'expenses/expense_list.html', {
        'expenses':          expenses,
        'categories':        categories,
        'towns':             towns,
        'selected_category': category_id,
        'selected_town':     town_id,
    })


@login_required
def expense_add(request):
    categories = ExpenseCategory.objects.all()
    towns      = Town.objects.filter(is_deleted=False).order_by('name')

    if request.method == 'POST':
        town_pk = request.POST.get('town')
        Expense.objects.create(
            category     = ExpenseCategory.objects.filter(
                               pk=request.POST.get('category')
                           ).first(),
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
    })

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, is_deleted=False)
    expense.is_deleted = True
    expense.save()
    messages.success(request, 'Expense deleted.')
    return redirect('expenses:expense_list')


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