from django.urls import path
from .views import (SavingListView, BalanceOfPaymentsView, BalanceRegistView,
                    M_DataView, BalanceEditView, BalanceDeleteView,
                    set_budget, set_goal, reset_goal, BudgetList, MonthlyComparisonView,
                    AddPaymentDestinationView)


app_name = 'household_budget'

urlpatterns = [
    path('b_regist/', BalanceRegistView.as_view(), name='b_regist'),
    path('balance/',BalanceOfPaymentsView.as_view(), name='balance'),
    path('savings/', SavingListView.as_view(), name='savings'),
    path('set_goal/', set_goal, name='set_goal'),
    path('reset_goal/', reset_goal, name='reset_goal'),
    path('monthly_data/<int:year>-<int:month>/', M_DataView.as_view(), name='monthly_data'),
    path('edit/<int:pk>/', BalanceEditView.as_view(), name='edit'),
    path('delete/<int:pk>/', BalanceDeleteView.as_view(), name='delete'),
    path('set_budget/', set_budget, name='set_budget'),
    path('budget_list/', BudgetList.as_view(), name='budget_list'),
    path('monthly-comparison/<int:year>/<int:month>/', MonthlyComparisonView.as_view(), name='monthly_comparison'),
    path('paymentdestination/', AddPaymentDestinationView.as_view(), name='paymentdestination'),

]
