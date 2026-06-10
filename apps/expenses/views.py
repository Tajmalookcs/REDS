from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expense, ExpenseCategory


@login_required
def expense_list(request):
    category_id = request.GET.get('category')
    expenses    = Expense.objects.filter(
                    is_deleted=False
                  ).select_related('category').order_by('-expense_date')
    categories  = ExpenseCategory.objects.all()

    if category_id:
        expenses = expenses.filter(category_id=category_id)

    return render(request, 'expenses/expense_list.html', {
        'expenses':          expenses,
        'categories':        categories,
        'selected_category': category_id,
    })


@login_required
def expense_add(request):
    categories = ExpenseCategory.objects.all()

    if request.method == 'POST':
        Expense.objects.create(
            category     = ExpenseCategory.objects.filter(
                               pk=request.POST.get('category')
                           ).first(),
            title        = request.POST.get('title'),
            amount       = request.POST.get('amount'),
            expense_date = request.POST.get('expense_date'),
            payment_mode = request.POST.get('payment_mode', 'CASH'),
            paid_to      = request.POST.get('paid_to', ''),
            cheque_no    = request.POST.get('cheque_no', ''),
            cheque_bank  = request.POST.get('cheque_bank', ''),
            cheque_date  = request.POST.get('cheque_date') or None,
            narration    = request.POST.get('narration', ''),
            image        = request.FILES.get('image'),   # ← ADD THIS
            created_by   = request.user,
        )
        messages.success(request, 'Expense recorded.')
        return redirect('expenses:expense_list')

    return render(request, 'expenses/expense_form.html', {
        'categories': categories,
        'title':      'Add Expense',
    })


@login_required
def expense_edit(request, pk):
    expense    = get_object_or_404(Expense, pk=pk, is_deleted=False)
    categories = ExpenseCategory.objects.all()

    if request.method == 'POST':
        expense.category     = ExpenseCategory.objects.filter(
                                   pk=request.POST.get('category')
                               ).first()
        expense.title        = request.POST.get('title')
        expense.amount       = request.POST.get('amount')
        expense.expense_date = request.POST.get('expense_date')
        expense.payment_mode = request.POST.get('payment_mode', 'CASH')
        expense.paid_to      = request.POST.get('paid_to', '')
        expense.cheque_no    = request.POST.get('cheque_no', '')
        expense.cheque_bank  = request.POST.get('cheque_bank', '')
        expense.cheque_date  = request.POST.get('cheque_date') or None
        expense.narration    = request.POST.get('narration', '')
        if request.FILES.get('image'):          # ← ADD THIS BLOCK
            expense.image = request.FILES.get('image')
        expense.save()
        messages.success(request, 'Expense updated.')
        return redirect('expenses:expense_list')

    return render(request, 'expenses/expense_form.html', {
        'expense':    expense,
        'categories': categories,
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