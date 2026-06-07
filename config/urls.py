from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import os
import signal
from django.http import HttpResponse

def shutdown(request):
    os.kill(os.getpid(), signal.SIGTERM)
    return HttpResponse("REDS is shutting down...")

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Core (dashboard, login, business profile, users, bank accounts)
    path('', include('apps.core.urls')),

    # Land (landlords, contracts, payment schedules)
    path('land/', include(('apps.land.urls', 'land'))),

    # Development (towns, blocks, plots)
    path('development/', include(('apps.development.urls', 'development'))),

    # Customers
    path('customers/', include(('apps.customers.urls', 'customers'))),

    # Agents
    path('agents/', include(('apps.agents.urls', 'agents'))),

    # Sales (bookings, receipts, cancellations)
    path('sales/', include('apps.sales.urls', 'sales')),

    # Expenses
    path('expenses/', include(('apps.expenses.urls', 'expenses'))),

    # Accounting (journal, ledger, reports)
    path('accounting/', include(('apps.accounting.urls', 'accounting'))),

    # Reports
    path('reports/', include(('apps.reports.urls', 'reports'))),
    # Shutdown URL (for development/testing purposes only)
    path('shutdown/', shutdown),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)