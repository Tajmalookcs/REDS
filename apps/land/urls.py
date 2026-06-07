from django.urls import path
from . import views

app_name = 'land'

urlpatterns = [
    # Landlords
    path('landlords/',              views.landlord_list,   name='landlord_list'),
    path('landlords/add/',          views.landlord_add,    name='landlord_add'),
    path('landlords/<int:pk>/edit/', views.landlord_edit,  name='landlord_edit'),
    path('landlords/<int:pk>/delete/', views.landlord_delete, name='landlord_delete'),

    # Contracts
    path('contracts/',              views.contract_list,   name='contract_list'),
    path('contracts/add/',          views.contract_add,    name='contract_add'),
    path('contracts/<int:pk>/edit/', views.contract_edit,  name='contract_edit'),
    path('contracts/<int:pk>/delete/', views.contract_delete, name='contract_delete'),

    # Payment Schedule
    path('contracts/<int:contract_pk>/schedule/', views.payment_schedule, name='payment_schedule'),
    path('contracts/<int:contract_pk>/schedule/add/', views.schedule_add, name='schedule_add'),
]