from django import forms
from .models import Transaction, Budget, Goal_Saving, Category, PaymentType, Vendor
from django.utils import timezone
from django.contrib.auth import get_user_model


#支払先登録
class VendorForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.all(), widget=forms.HiddenInput(), required=False)
    vendor_name = forms.CharField(label='支払先')
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(VendorForm, self).__init__(*args, **kwargs)
        
        if user and user.is_authenticated:
            self.fields['user'].initial = user
            self.fields['user'].queryset = get_user_model().objects.filter(pk=user.pk)
            
    
    class Meta:
        model = Vendor
        fields = ['vendor_name']        

#支出登録
class TransactionForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.all(), widget=forms.HiddenInput(), required=False)
    event_date = forms.DateField(
        label='日付',
        initial=timezone.now().date(),
        widget=forms.SelectDateWidget(years=range(timezone.now().year - 5, timezone.now().year + 2))
    )
    name_1 = forms.CharField(label='本人名', required=False)
    name_2 = forms.CharField(label='パートナー名', required=False)
    category = forms.ModelChoiceField(label='項目', queryset=Category.objects.all())
    payment_type = forms.ModelChoiceField(label='収支種別', queryset=PaymentType.objects.all())
    amount = forms.IntegerField(label='金額')
    memo = forms.CharField(label='メモ', widget=forms.Textarea, required=False)
    vendor_name = forms.ModelChoiceField(label='支払先', queryset=Vendor.objects.all())
    
    def clean_event_date(self):
        return self.cleaned_data.get('event_date')
        
    def clean_vendor_name(self):
        vendor = self.cleaned_data.get('vendor_name')
        if vendor:
            return vendor
        return None

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(TransactionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Transaction
        fields = ['event_date', 'name_1', 'name_2', 'category', 'payment_type', 'vendor_name', 'amount', 'memo']
  

 #年月入力       
class YearMonthField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(),
            forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 13)]),
        )
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return f"{data_list[0]:04d}-{data_list[1]:02d}"
        return None

#貯金目標

class MonthField(forms.DateField):
    widget = forms.TextInput(attrs={'type': 'month'})
    
class SavingForm(forms.ModelForm):
    savings_goal = forms.IntegerField(label='目標', initial=0)
    month = forms.DateField(label='入力日', initial=timezone.now().date())

    class Meta:
        model = Goal_Saving
        fields = ['month', 'savings_goal']   
                
        
#予算設定
class BudgetForm(forms.ModelForm):
    event_date = forms.DateField(label='日付', initial=timezone.now().date())
    rent_budget = forms.IntegerField(label='家賃', initial=0)
    water_supply_budget = forms.IntegerField(label='水道代', initial=0)
    gas_budget = forms.IntegerField(label='ガス代', initial=0)
    electricity_budget = forms.IntegerField(label='電気代', initial=0)
    food_expenses_budget = forms.IntegerField(label='食費', initial=0)
    communication_expenses_budget = forms.IntegerField(label='通信費', initial=0)
    transportation_expenses_budget = forms.IntegerField(label='交通費', initial=0)
    insurance_fee_budget = forms.IntegerField(label='保険料', initial=0)
    daily_necessities_budget = forms.IntegerField(label='日用品', initial=0)
    medical_bills_budget = forms.IntegerField(label='医療費', initial=0)
    entertainment_expenses_budget = forms.IntegerField(label='交際費', initial=0)
    saving_budget = forms.IntegerField(label='貯金', initial=0)
    add_item_budget = forms.IntegerField(label='その他', initial=0)
    
    class Meta:
        model = Budget
        fields = ['event_date', 'rent_budget', 'water_supply_budget', 'gas_budget', 'electricity_budget', 'food_expenses_budget', 'communication_expenses_budget', 'transportation_expenses_budget', 'insurance_fee_budget', 'daily_necessities_budget', 'medical_bills_budget', 'entertainment_expenses_budget', 'saving_budget', 'add_item_budget']

