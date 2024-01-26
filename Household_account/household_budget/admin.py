from django.contrib import admin
from .models import(Transaction, Vendor, Category, PaymentType)

admin.site.register([Transaction, Vendor, Category, PaymentType])