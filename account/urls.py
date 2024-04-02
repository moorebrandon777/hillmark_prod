from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'account'

urlpatterns = [
    # admin part
    path('admin_dashboard/', views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path('admin_customer_detail/<pk>/', views.CustomerDetailsAdminView.as_view(), name="admin_customer_detail"),
    path('activate_customer/<pk>/', views.activate_and_deactivate_customer_account, name="activate_customer"),
    path('activate_transaction_status/<pk>/', views.admin_transaction_success_or_fail, name="activate_transaction_status"),
    path('update_customer/<pk>/', views.UpdateCustomerView.as_view(), name="update_customer"),
    path('admin_change_customer_password/<pk>/', views.admin_change_customer_password, name="admin_change_customer_password"),
    path('admin_delete_customer/<pk>/', views.admin_delete_customer, name="admin_delete_customer"),

    # cutomer part
    path('customer_dashboard/', views.CustomerDashboardView.as_view(), name="customer_dashboard"),
    path('customer_care/', views.CustomerCareView.as_view(), name="customer_care"),
    path('customer_ewallet/', views.CustomerEwalleteView.as_view(), name="customer_ewallet"),
    path('customer_settings/', views.CustomerSettingsView.as_view(), name="customer_settings"),
    path('customer_transactions/', views.CustomerAllTransactionsView.as_view(), name="customer_transactions"),

    path('logout/', LogoutView.as_view(next_page='frontend:login'),name='logout'),
    
]