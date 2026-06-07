from django.urls import path
from apps.accounting import views

urlpatterns = [
    # Chart of Accounts
    path('accounts/',                   views.account_list,   name='account_list'),
    path('accounts/add/',               views.account_add,    name='account_add'),
    path('accounts/<int:pk>/edit/',     views.account_edit,   name='account_edit'),

    # Journal Entries
    path('journal/',                    views.journal_list,   name='journal_list'),
    path('journal/add/',                views.journal_add,    name='journal_add'),
    path('journal/<int:pk>/',           views.journal_detail, name='journal_detail'),

    # Accounting Reports
    path('cash-book/',                  views.cash_book,      name='cash_book'),
    path('general-ledger/',             views.general_ledger, name='general_ledger'),
    path('trial-balance/',              views.trial_balance,  name='trial_balance'),
    path('bank-ledger/',                views.bank_ledger, name='bank_ledger'),
]