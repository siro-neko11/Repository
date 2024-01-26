from django.contrib import admin
from .models import(Transaction, Vendor, Category)

admin.site.register([Transaction, Vendor, Category])