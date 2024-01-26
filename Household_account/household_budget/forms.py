from django import forms
from .models import Transaction, Budget, Goal_Saving, Category, PaymentType, Vendor
from django.utils import timezone
from django.contrib.auth import get_user_model


#支払先登録
class VendorForm(forms.ModelForm):
    vendor_name = forms.CharField(label='支払先')
    
    class Meta:
        model = Vendor
        fields = ['vendor_name']        

#支出登録
class TransactionForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.all(), widget=forms.HiddenInput())
    event_date = forms.DateField(
        label='日付',
        initial=timezone.now().date(),
        widget=forms.SelectDateWidget(years=range(timezone.now().year - 5, timezone.now().year + 2))
    )
    name_1 = forms.CharField(label='本人名', required=False)
    name_2 = forms.CharField(label='パートナー名', required=False)
    category = forms.ModelChoiceField(label='項目', queryset=Category.objects.all())
    payment_type = forms.ModelChoiceField(label='支払い種別', queryset=PaymentType.objects.all())
    vendor_name = forms.ModelChoiceField(label='支払先', queryset=Vendor.objects.all(), widget=forms.Select)
    amount = forms.IntegerField(label='金額')
    memo = forms.CharField(label='メモ', widget=forms.Textarea)

    # VendorFormを追加する代わりに、VendorFormのフィールドを直接追加する
    vendor_name_form = forms.CharField(label='支払先', max_length=50)

    def __init__(self, user, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Transaction
        fields = ['event_date', 'name_1', 'name_2', 'category', 'payment_type', 'amount', 'memo']

# #収支登録画面
# #金額入力
# class BalanceOfPaymentsForm(forms.ModelForm):
#     user = forms.ModelChoiceField(queryset=get_user_model().objects.all(), widget=forms.HiddenInput())
#     event_date = forms.DateField(label='日付', initial=timezone.now().date(), widget=forms.SelectDateWidget(years=range(timezone.now().year - 5, timezone.now().year + 2)))
#     name_1 = forms.CharField(label='本人名', required=False)
#     name_2 = forms.CharField(label='パートナー名', required=False)
#     income = forms.IntegerField(label='収入', initial=0)
#     rent = forms.IntegerField(label='家賃', initial=0)
#     water_supply = forms.IntegerField(label='水道代', initial=0)
#     gas = forms.IntegerField(label='ガス代', initial=0)
#     electricity = forms.IntegerField(label='電気代', initial=0)
#     food_expenses = forms.IntegerField(label='食費', initial=0)
#     communication_expenses = forms.IntegerField(label='通信費', initial=0)
#     transportation_expenses = forms.IntegerField(label='交通費', initial=0)
#     insurance_fee = forms.IntegerField(label='保険代', initial=0)
#     daily_necessities = forms.IntegerField(label='日用品', initial=0)
#     medical_bills = forms.IntegerField(label='医療費', initial=0)
#     entertainment_expenses = forms.IntegerField(label='交際費', initial=0)
#     saving = forms.IntegerField(label='貯金', initial=0)
#     add_item = forms.IntegerField(label='その他', initial=0)


#     # 項目選択
#     ITEM = (
#         ('incom', '収入'), ('rent', '家賃'), ('water_supply', '水道代'), ('gas', 'ガス代'), ('electricity', '電気代'),
#         ('food_expenses', '食費'), ('communication_expenses', '通信費'), ('transportation_expenses', '交通費'), 
#         ('insurance_fee', '保険代'), ('daily_necessities', '日用品'), ('medical_bills', '医療費'), 
#         ('entertainment_expenses', '交際費'), ('saving', '貯金'), ('add_item', 'その他'),
#     )
        
#     item = forms.ChoiceField(label='項目', choices=ITEM, initial='food_expenses')
    
#     # 支払先選択
#     payment_destination = forms.ChoiceField(label='支払先', choices=[], required=False)
#     #支払い種別選択
#     payment_type = forms.ChoiceField(label='支払種別', choices=[], required=False)


#     def __init__(self, user, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['user'].initial = user
#         self.fields['user'].widget = forms.HiddenInput()
#         self.fields['payment_destination'].choices = self.get_payment_destination_choices()
#         self.fields['payment_type'].choices = self.get_payment_type_choices()
        
#     def get_payment_type_choices(self):
#         payment_types = PaymentDestination.objects.all()
#         choices = [(type.payment_type, type.payment_type) for type in payment_types]
#         return choices

#     def get_payment_destination_choices(self):
#         # データベースからユーザーが入力した支払先を取得し、選択肢にセット
#         custom_items = CustomItemPaymentdestination.objects.filter(user=self.fields['user'].initial)
#         choices = [(item.payment_destination, item.payment_destination) for item in custom_items]
#         return choices
    


#     class Meta:
#         model = BalanceOfPayments
#         fields = ['name_1', 'name_2', 'income', 'rent', 'water_supply',
#                   'gas', 'electricity', 'food_expenses', 'communication_expenses', 
#                   'transportation_expenses', 'insurance_fee', 'daily_necessities',
#                   'medical_bills', 'entertainment_expenses', 'saving', 'add_item',
#                   'payment_destination','payment_type']        


    

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

