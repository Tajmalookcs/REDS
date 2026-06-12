from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [

    # ── Bookings ───────────────────────────────────────
    path('bookings/',                       views.booking_list,   name='booking_list'),
    path('bookings/add/',                   views.booking_add,    name='booking_add'),
    path('bookings/<int:pk>/',              views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/edit/',         views.booking_edit,   name='booking_edit'),
    path('bookings/<int:pk>/delete/',       views.booking_delete, name='booking_delete'),
    path('bookings/<int:pk>/cancel/',       views.booking_cancel, name='booking_cancel'),
    path('bookings/<int:pk>/possession/',   views.booking_possession, name='booking_possession'),
    path('bookings/<int:pk>/registry/',     views.booking_registry,   name='booking_registry'),
    path('bookings/<int:booking_id>/transfer/', views.transfer_create, name='transfer_create'),
    # ── Payment Plan ───────────────────────────────────
    path('bookings/<int:booking_pk>/plan/add/', views.plan_add,  name='plan_add'),

    # ── Receipts ───────────────────────────────────────
    path('bookings/<int:booking_pk>/receipt/add/', views.receipt_add, name='receipt_add'),
    path('receipts/', views.receipt_list,   name='receipt_list'),
    path('receipts/<int:pk>/print/', views.receipt_print, name='receipt_print'),
    path('bookings/<int:pk>/print/', views.booking_print, name='booking_print'),
    path('cancellations/<int:pk>/refund/', views.refund_pay, name='refund_pay'),
    path('refund-receipts/<int:pk>/print/', views.refund_receipt_print, name='refund_receipt_print'),
    path('refunds/', views.refund_list, name='refund_list'),

]