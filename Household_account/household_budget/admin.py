from django.contrib import admin
from .models import(Transaction, Vendor)

admin.site.register([Transaction, Vendor])