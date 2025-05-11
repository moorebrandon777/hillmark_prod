from django.urls import path

from . import views

app_name = 'transactions'

urlpatterns = [
    path("deposit/", views.DepositMoneyView.as_view(), name="deposit_money"),
    path("withdraw/", views.WithdrawMoneyView.as_view(), name="withdraw_money"),
    # path("account/all_transactions/", views.TransactionListView.as_view(), name="all_transactions"),
    path("account/all_transactions/", views.all_transaction_list, name="all_transactions"),
    path("delete_transaction/<pk>/", views.delete_transaction, name="delete_transaction"),

    path("delete_customer_transaction/<pk>/", views.delete_single_customer_transaction, name="delete_customer_transaction"),
    
    path("account/transfer/", views.CustomerWithdrawMoneyView.as_view(), name="customer_transfer"),
    path("transaction_successful/", views.transaction_successful, name="transaction_successful"),
    path("transaction_failed/", views.transaction_failed, name="transaction_failed"),
]