from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reservations/', views.reservations, name='reservations'),
    path('orders/', views.order_list, name='orders'),
    path('items/', views.items_view, name='items'),
    path('payments/', views.payments, name='payments'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('items/', views.item_list, name='item_list'),
    path('create-reservation/', views.create_reservation, name='create_reservation'),
    path('reservations/', views.reservations_view, name='reservations'),
    
    # modal handlers
    path('login/', views.login_modal, name='login'),
    path('register/', views.register_modal, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin dashboard routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('admin-dashboard/orders/update/<int:order_id>/<str:status>/', views.admin_update_order_status, name='admin_update_order_status'),
    path('admin-dashboard/reservations/', views.admin_reservations, name='admin_reservations'),
    path('admin-dashboard/reservations/update/<int:reservation_id>/<str:status>/', views.admin_update_reservation_status, name='admin_update_reservation_status'),
    path('admin-dashboard/items/', views.admin_items, name='admin_items'),
    path('admin-dashboard/items/add/', views.admin_add_item, name='admin_add_item'),
    path('admin-dashboard/items/edit/<int:item_id>/', views.admin_edit_item, name='admin_edit_item'),
    path('admin-dashboard/items/delete/<int:item_id>/', views.admin_delete_item, name='admin_delete_item'),
    path('admin-dashboard/customers/', views.admin_customers, name='admin_customers'),
    path('admin-dashboard/customers/<int:customer_id>/', views.admin_customer_detail, name='admin_customer_detail'),
    path('admin-dashboard/payments/', views.admin_payments, name='admin_payments'),
    path('admin-dashboard/payments/<int:payment_id>/', views.admin_payment_detail, name='admin_payment_detail'),
    
    # Table reservation routes
    path('reserve-table/', views.table_reservation_form, name='table_reservation_form'),
    path('cancel-table-reservation/<int:reservation_id>/', views.cancel_table_reservation, name='cancel_table_reservation'),
    path('admin-dashboard/table-reservations/update/<int:reservation_id>/<str:status>/', views.admin_update_table_reservation_status, name='admin_update_table_reservation_status'),
]
