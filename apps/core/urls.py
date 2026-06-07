from django.urls import path
from . import views

urlpatterns = [
    path('',                                views.dashboard,             name='dashboard'),
    path('login/',                          views.login_view,            name='login'),
    path('login/validate-credentials/',     views.validate_credentials,  name='validate_credentials'),
    path('logout/',                         views.logout_view,           name='logout'),
    path('business-profile/',               views.business_profile,      name='business_profile'),
    path('bank-accounts/',                  views.bank_account_list,     name='bank_account_list'),
    path('bank-accounts/add/',              views.bank_account_add,      name='bank_account_add'),
    path('bank-accounts/<int:pk>/edit/',    views.bank_edit,             name='bank_edit'),
    path('bank-accounts/<int:pk>/delete/',  views.bank_delete,           name='bank_delete'),
    path('users/',                          views.user_list,             name='user_list'),
    path('users/add/',                      views.user_add,              name='user_add'),
    path('users/<int:pk>/edit/',            views.user_edit,             name='user_edit'),
    path('users/<int:pk>/password/',        views.user_change_password,  name='user_change_password'),
    path('users/<int:pk>/toggle/',          views.user_toggle,           name='user_toggle'),
    path('users/<int:pk>/delete/',          views.user_delete,           name='user_delete'),
]