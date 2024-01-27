from django.urls import path
from .views import (SavingListView, TransactionView, TransactionRegistView,
                    M_DataView, BalanceDeleteView, edit_transaction,
                    set_budget, set_goal, reset_goal, MonthlyComparisonView,
                    AddPaymentDestinationView, UpdatePaymentDestinationView, DeletePaymentDestinationView,
                    PaymentDestinationListView)


app_name = 'household_budget'

urlpatterns = [
    path('b_regist/', TransactionRegistView.as_view(), name='b_regist'),
    path('balance/',TransactionView.as_view(), name='balance'),
    path('savings/', SavingListView.as_view(), name='savings'),
    path('set_goal/', set_goal, name='set_goal'),
    path('reset_goal/', reset_goal, name='reset_goal'),
    path('monthly_data/<int:year>-<int:month>/', M_DataView.as_view(), name='monthly_data'),
    # path('edit_transaction/<int:transaction_id>/', edit_transaction, name='edit_transaction'),
    # path('edit_transaction/<int:pk>/', BalanceEditView.as_view(), name='edit_transaction'),
    path('balance/edit/<int:transaction_id>/', edit_transaction, name='edit_transaction'),
    path('delete/<int:pk>/', BalanceDeleteView.as_view(), name='delete'),
    path('set_budget/', set_budget, name='set_budget'),
    path('monthly-comparison/<int:year>/<int:month>/', MonthlyComparisonView.as_view(), name='monthly_comparison'),
    path('paymentdestination/', AddPaymentDestinationView.as_view(), name='paymentdestination'),
    path('updatepaymentdestination/<int:pk>/', UpdatePaymentDestinationView.as_view(), name='updatepaymentdestination'),
    path('deletepaymentdestination/<int:pk>/', DeletePaymentDestinationView.as_view(), name='deletepaymentdestination'),
    path('paymentdestination/list/', PaymentDestinationListView.as_view(), name='payment_destination_list'),
    ]
