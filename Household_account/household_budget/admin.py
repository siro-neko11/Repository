from django.contrib import admin
from .models import(BalanceOfPayments, PaymentDestination)

admin.site.register([BalanceOfPayments, PaymentDestination])