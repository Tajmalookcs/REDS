from django.urls import path
from apps.reports import views

urlpatterns = [
    path('sales/',      views.sales_summary,   name='sales_summary'),
    path('plots/',      views.plot_availability, name='plot_availability'),
    path('ledger/',     views.customer_ledger,  name='customer_ledger'),
    path('commission/', views.agent_commission, name='agent_commission'),
    path('expenses/',   views.expense_summary,  name='expense_summary'),
    path('landlord/', views.landlord_report, name='landlord_report'),
    path('cash-bank/', views.cash_bank_position, name='cash_bank_position'),
    path('profit-loss/', views.profit_loss, name='profit_loss'),
    path('tax-summary/', views.tax_summary, name='tax_summary'),

]