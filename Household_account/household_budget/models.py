from django.db import models 
from django.utils import timezone
from django.conf import settings
import datetime
from django import forms


#項目
class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name
    
    class Meta:
        db_table = 'category'
    
    
#支払い種別
class PaymentType(models.Model):
    payment_type = models.CharField(max_length=20)
    
    def __str__(self):
        return self.payment_type
    
    class Meta:
        db_table = 'pament_type'    
        
        
#支払先登録
class Vendor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)

    def __str__(self):
        return self.vendor_name
    
    class Meta:
        db_table = 'vendor'
             

#収支入力画面
class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_date = models.DateField()
    name_1 = models.CharField(max_length=20, default='', null=True)
    name_2 = models.CharField(max_length=20, default='', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    vendor_name = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_transactions')
    amount = models.IntegerField(default=0)
    memo = models.TextField(null=True)
    
    class Meta:
        db_table = 'transaction'
        ordering = ['event_date']

    
#予算設定
class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_date = models.DateField(default=datetime.date.today)
    rent_budget = models.IntegerField(default=0)
    water_supply_budget = models.IntegerField(default=0)
    gas_budget = models.IntegerField(default=0)
    electricity_budget = models.IntegerField(default=0)
    food_expenses_budget = models.IntegerField(default=0)
    communication_expenses_budget = models.IntegerField(default=0)
    transportation_expenses_budget = models.IntegerField(default=0)
    insurance_fee_budget = models.IntegerField(default=0)
    daily_necessities_budget = models.IntegerField(default=0)
    medical_bills_budget = models.IntegerField(default=0)
    entertainment_expenses_budget = models.IntegerField(default=0)
    saving_budget = models.IntegerField(default=0)
    add_item_budget = models.IntegerField(default=0)

    class Meta:
        db_table = 'Budget'
        
    @property
    def year(self):
        return self.event_date.year

    @property
    def month(self):
        return self.event_date.month
              

#日付取得                
class MonthField(models.DateField):
    def formfield(self, **kwargs):
        defaults = {'form_class': forms.DateField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


# 貯金目標
class Goal_Saving(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=True)
    month = models.DateField(default=timezone.now)
    savings_goal = models.IntegerField(null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        username = self.user.username if self.user is not None else "N/A"
        return f"{username} - {self.month.strftime('%m')}"

    class Meta:
        db_table = 'goal_saving'
