from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import BusinessProfileForm, BankAccountForm
from .models import BusinessProfile, BankAccount, CustomUser
from django.db.models import Sum
from apps.development.models import Plot
from apps.sales.models import Booking, PaymentPlan, Receipt, Cancellation
from datetime import date, timedelta

# ======================================================
# LOGIN
# ======================================================

@require_http_methods(["POST"])
def validate_credentials(request):
    """AJAX endpoint to validate credentials before starting timer"""
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    
    if not username or not password:
        return JsonResponse({
            'valid': False,
            'error': 'Username and password are required.'
        })
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        return JsonResponse({'valid': True})
    else:
        return JsonResponse({
            'valid': False,
            'error': 'Invalid username or password.'
        })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# ======================================================
# DASHBOARD
# ======================================================

@login_required
@login_required
def dashboard(request):
    today = date.today()
    
    # ── Existing KPIs ──────────────────────────────────
    total_plots     = Plot.objects.filter(is_deleted=False).count()
    available_plots = Plot.objects.filter(is_deleted=False, status='AVAILABLE').count()
    bookings        = Booking.objects.filter(is_deleted=False)
    active_bookings = bookings.filter(status='ACTIVE').count()
    total_received  = Receipt.objects.filter(is_deleted=False).aggregate(total=Sum('amount'))['total'] or 0
    receipts_today  = Receipt.objects.filter(is_deleted=False, receipt_date=today).count()

    overdue_installments  = PaymentPlan.objects.filter(status='OVERDUE')
    due_soon_installments = PaymentPlan.objects.filter(
        status='PENDING',
        due_date__gt=today,
        due_date__lte=today + timedelta(days=7),
    )
    red_count    = overdue_installments.count()
    yellow_count = due_soon_installments.count()

    # ── Towns with stats ───────────────────────────────
    from apps.development.models import Town, Block, TownMap, Block as _Block
    from django.db.models import Count, Q

    all_towns  = Town.objects.filter(is_deleted=False).order_by('name')
    all_blocks = _Block.objects.filter(is_deleted=False).select_related('town').order_by('town__name', 'name')

    towns_data = []
    towns = all_towns.prefetch_related('blocks', 'maps')

    for town in towns:
        # Get all plots for this town
        town_plots = Plot.objects.filter(
            block__town=town,
            is_deleted=False
        )
        total   = town_plots.count()
        sold    = town_plots.filter(status='SOLD').count()
        booked  = town_plots.filter(status='BOOKED').count()
        avail   = town_plots.filter(status='AVAILABLE').count()
        hold    = town_plots.filter(status='HOLD').count()

        # Get town image from maps
        town_image = town.maps.filter(
            map_type='IMAGE',
            is_active=True
        ).first()

        towns_data.append({
            'town':       town,
            'total':      total,
            'sold':       sold,
            'booked':     booked,
            'available':  avail,
            'hold':       hold,
            'image':      town_image,
        })

    # ── Plots detail — all plots with booking financials ──
    from apps.sales.models import Booking as _Booking
    from django.db.models import Sum as _Sum
    _booking_map = {
        b.plot_id: b
        for b in _Booking.objects
            .filter(is_deleted=False, status__in=['ACTIVE', 'COMPLETED'])
            .annotate(amount_received=_Sum('receipts__amount'))
    }
    import re as _re
    def _nat_key(d):
        parts = _re.split(r'(\d+)', d['plot_no'])
        return [int(p) if p.isdigit() else p.lower() for p in parts]

    _all_plots = (
        Plot.objects
        .filter(is_deleted=False)
        .select_related('block__town')
        .order_by('block__town__name', 'block__name')
    )
    plots_detail         = []
    plots_total_net      = 0
    plots_total_received = 0
    plots_total_marla    = 0
    for p in _all_plots:
        bk       = _booking_map.get(p.pk)
        net      = (bk.net_price or 0) if bk else (p.price or 0)
        received = (bk.amount_received or 0) if bk else 0
        balance  = net - received
        size     = float(p.size or 0)
        plots_total_net      += net
        plots_total_received += received
        plots_total_marla    += size
        plots_detail.append({
            'plot_no':   p.plot_no,
            'block':     p.block.name,
            'town':      p.block.town.name,
            'status':    p.status,
            'customer':  bk.customer.name if bk else '—',
            'net_price': net,
            'received':  received,
            'balance':   balance,
            'size':      size,
            'size_unit': p.size_unit,
        })
    plots_detail.sort(key=lambda d: (d['town'], d['block'], _nat_key(d)))
    plots_total_balance = plots_total_net - plots_total_received

    context = {
        'total_plots':            total_plots,
        'available_plots':        available_plots,
        'active_bookings':        active_bookings,
        'total_received':         total_received,
        'receipts_today':         receipts_today,
        'red_count':              red_count,
        'yellow_count':           yellow_count,
        'overdue_installments':   overdue_installments,
        'due_soon_installments':  due_soon_installments,
        'towns_data':             towns_data,
        'plots_detail':           plots_detail,
        'plots_total_net':        plots_total_net,
        'plots_total_received':   plots_total_received,
        'plots_total_balance':    plots_total_balance,
        'plots_total_marla':      plots_total_marla,
        'all_towns':              all_towns,
        'all_blocks':             all_blocks,
    }
    return render(request, 'core/dashboard.html', context)


# ======================================================
# LOGOUT
# ======================================================

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def stop_server(request):
    import threading, os, signal
    def _shutdown():
        import time
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)
    threading.Thread(target=_shutdown, daemon=True).start()
    return render(request, 'core/server_stopped.html')


# ======================================================
# BUSINESS PROFILE
# ======================================================

@login_required
def business_profile(request):
    if request.user.role != 'SUPERUSER':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    profile = BusinessProfile.objects.first()
    form = BusinessProfileForm(instance=profile)

    if request.method == 'POST':
        form = BusinessProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Business profile updated.')
            return redirect('business_profile')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'core/business_profile.html', {
        'profile': profile,
        'form': form,
    })


# ======================================================
# BANK ACCOUNTS
# ======================================================

@login_required
def bank_account_list(request):
    if request.user.role != 'SUPERUSER':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    accounts = BankAccount.objects.filter(is_active=True)
    form = BankAccountForm()
    return render(request, 'core/bank_account.html', {
        'accounts': accounts,
        'form': form,
    })


@login_required
def bank_account_add(request):
    if request.user.role != 'SUPERUSER':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    form = BankAccountForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Bank account added.')
        return redirect('bank_account_list')

    return render(request, 'core/bank_account_form.html', {'form': form, 'title': 'Add Bank Account'})


@login_required
def bank_edit(request, pk):
    if request.user.role != 'SUPERUSER':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    account = get_object_or_404(BankAccount, pk=pk)
    form = BankAccountForm(request.POST or None, instance=account)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Bank account updated.')
        return redirect('bank_account_list')

    return render(request, 'core/bank_account_form.html', {
        'form': form,
        'title': 'Edit Bank Account',
    })


@login_required
def bank_delete(request, pk):
    if request.user.role != 'SUPERUSER':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    account = get_object_or_404(BankAccount, pk=pk)
    account.delete()
    messages.success(request, 'Bank account deleted.')
    return redirect('bank_account_list')


# ======================================================
# USER MANAGEMENT
# ======================================================


from django.contrib.auth.hashers import make_password

# ======================================================
# USER MANAGEMENT
# ======================================================

@login_required
def user_list(request):
    if request.user.role != 'SUPERUSER':
        return redirect('dashboard')
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'core/user_list.html', {'users': users})


@login_required
def user_add(request):
    if request.user.role != 'SUPERUSER':
        return redirect('dashboard')
    if request.method == 'POST':
        username  = request.POST.get('username')
        full_name = request.POST.get('full_name')
        role      = request.POST.get('role')
        password  = request.POST.get('password')
        is_active = 'is_active' in request.POST

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
            return render(request, 'core/user_form.html', {
                'title': 'Add User',
                'post': request.POST,
            })

        is_superuser = role == 'SUPERUSER'
        CustomUser.objects.create(
            username     = username,
            full_name    = full_name,
            role         = role,
            is_active    = is_active,
            is_staff     = is_superuser,
            is_superuser = is_superuser,
            password     = make_password(password),
        )
        messages.success(request, f'User "{username}" created successfully.')
        return redirect('user_list')

    return render(request, 'core/user_form.html', {
        'title': 'Add User',
        'post': {
            'username': '',
            'full_name': '',
            'role': 'USER',
        },
    })


@login_required
def user_edit(request, pk):
    if request.user.role != 'SUPERUSER':
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        user.full_name = request.POST.get('full_name')
        user.role      = request.POST.get('role')
        user.is_active = 'is_active' in request.POST
        if user.role == 'SUPERUSER':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_superuser = False
        user.save()
        messages.success(request, f'User "{user.username}" updated.')
        return redirect('user_list')

    return render(request, 'core/user_form.html', {
        'title': 'Edit User',
        'user_obj': user,
        'post': {
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role,
        },
    })


@login_required
def user_change_password(request, pk):
    if request.user.role != 'SUPERUSER':
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm  = request.POST.get('confirm')
        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'core/user_password.html', {'user_obj': user})
        user.password = make_password(password)
        user.save()
        messages.success(request, f'Password changed for "{user.username}".')
        return redirect('user_list')

    return render(request, 'core/user_password.html', {'user_obj': user})


@login_required
def user_toggle(request, pk):
    if request.user.role != 'SUPERUSER':
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('user_list')
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" {status}.')
    return redirect('user_list')


@login_required
def user_delete(request, pk):
    if request.user.role != 'SUPERUSER':
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_list')
    if user.role == 'SUPERUSER':
        messages.error(request, 'Cannot delete a Superuser account.')
        return redirect('user_list')
    username = user.username
    user.delete()
    messages.success(request, f'User "{username}" deleted.')
    return redirect('user_list')