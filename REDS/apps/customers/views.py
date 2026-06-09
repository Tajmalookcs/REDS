from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer


@login_required
def customer_list(request):
    query     = request.GET.get('q', '')
    customers = Customer.objects.filter(is_deleted=False).order_by('-created_at')

    if query:
        customers = customers.filter(name__icontains=query) | \
                    customers.filter(contact__icontains=query) | \
                    customers.filter(cnic__icontains=query)

    return render(request, 'customers/customer_list.html', {
        'customers': customers,
        'query':     query,
    })


@login_required
def customer_add(request):
    if request.method == 'POST':
        Customer.objects.create(
            name       = request.POST.get('name'),
            name_urdu  = request.POST.get('name_urdu', ''),
            contact    = request.POST.get('contact'),
            cnic       = request.POST.get('cnic', ''),
            address    = request.POST.get('address', ''),
            city       = request.POST.get('city', ''),
            email      = request.POST.get('email', ''),
            created_by = request.user,
        )
        messages.success(request, 'Customer added successfully.')
        return redirect('customers:customer_list')

    return render(request, 'customers/customer_form.html', {
        'title': 'Add Customer'
    })


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk, is_deleted=False)

    if request.method == 'POST':
        customer.name      = request.POST.get('name')
        customer.name_urdu = request.POST.get('name_urdu', '')
        customer.contact   = request.POST.get('contact')
        customer.cnic      = request.POST.get('cnic', '')
        customer.address   = request.POST.get('address', '')
        customer.city      = request.POST.get('city', '')
        customer.email     = request.POST.get('email', '')
        customer.save()
        messages.success(request, 'Customer updated.')
        return redirect('customers:customer_list')

    return render(request, 'customers/customer_form.html', {
        'customer': customer,
        'title':    'Edit Customer',
    })


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk, is_deleted=False)
    customer.is_deleted = True
    customer.save()
    messages.success(request, 'Customer deleted.')
    return redirect('customers:customer_list')