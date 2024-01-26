from django.shortcuts import render,redirect, get_object_or_404
from django.db.models import Sum
from .models import Transaction, Budget, Goal_Saving, Vendor
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm, SavingForm, BudgetForm, VendorForm
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.generic.base import  View
from django.http.response import HttpResponse as HttpResponse
from datetime import datetime, timedelta
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages


# 収支登録画面
class TransactionRegistView(View):
    template_name = 'b_regist.html'
    form_class = TransactionForm

    def get(self, request, *args, **kwargs):
        transactions = Transaction.objects.all()
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'transactions': transactions, 'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            # 保存処理などを追加
            form.save()
            return redirect('household_budget:b_regist')  # 保存後に収支登録画面にリダイレクト
        else:
            transactions = Transaction.objects.all()
            return render(request, self.template_name, {'transactions': transactions, 'form': form})    
        
        
#     def get(self, request, *args, **kwargs):
#         last_entry = Transaction.objects.filter(user=request.user).last()
#         initial_data = {'name_1': last_entry.name_1, 'name_2': last_entry.name_2} if last_entry else {}
#         form = self.form_class(user=request.user, initial=initial_data)
#         return render(request, self.template_name, {'form': form})
    
#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.user, request.POST)
#         if form.is_valid():
#             name_1 = form.cleaned_data['name_1']
#             name_2 = form.cleaned_data['name_2']
            
#             payment_destination = form.cleaned_data['payment_destination']

#             if name_1 or name_2:
#                 instance = form.save(commit=False)
#                 instance.user = request.user
#                 instance.payment_destination = payment_destination  # フォームから直接取得するように修正
#                 instance.save()
#                 messages.success(request, '収支データが保存されました。')
#                 return redirect('accounts:user')
#             else:
#                 messages.error(request, '名前１または名前２のどちらか一方は入力してください。')
#         else:
#             messages.error(request, 'エラーが発生しました。データは保存されませんでした.')
        
#         return render(request, self.template_name, {'form': form})
    

#支払先登録
class AddPaymentDestinationView(View):
    template_name = 'add_payment_destination.html'

    def get(self, request):
        form = VendorForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = VendorForm(request.POST)
        if form.is_valid():
            # フォームが妥当であればデータベースに新しい支払先を追加
            payment_destination = form.cleaned_data['payment_destination']
            user = request.user
            Vendor.objects.create(user=user, payment_destination=payment_destination)
            return redirect('household_budget:b_regist')

        return render(request, self.template_name, {'form': form})


# 支払先編集
class UpdatePaymentDestinationView(View):
    template_name = 'update_paymentdestination.html'
    form_class = VendorForm

    def get(self, request, pk, *args, **kwargs):
        payment_destination = Vendor.objects.get(pk=pk)
        form = self.form_class(instance=payment_destination)
        return render(request, self.template_name, {'form': form, 'payment_destination': payment_destination})

    def post(self, request, pk, *args, **kwargs):
        payment_destination = Vendor.objects.get(pk=pk)
        form = self.form_class(request.POST, instance=payment_destination)
        if form.is_valid():
            form.save()
            return redirect('household_budget:b_regist')
        return render(request, self.template_name, {'form': form, 'payment_destination': payment_destination})

# 支払先削除
class DeletePaymentDestinationView(View):
    template_name = 'delete_paymentdestination.html'

    def get(self, request, pk, *args, **kwargs):
        payment_destination = Vendor.objects.get(pk=pk)
        return render(request, self.template_name, {'payment_destination': payment_destination})

    def post(self, request, pk, *args, **kwargs):
        payment_destination = Vendor.objects.get(pk=pk)
        payment_destination.delete()
        return redirect('household_budget:b_regist')
    
#支払先一覧
class PaymentDestinationListView(View):
    template_name = 'payment_destination_list.html'

    def get(self, request):
        if request.user.is_authenticated:
            payment_destinations = Vendor.objects.filter(user=request.user)
            return render(request, self.template_name, {'payment_destinations': payment_destinations})
        else:
            # ユーザーが認証されていない場合は、ログインページなどへリダイレクトするか、エラーを表示するなどの処理を行います
            return render(request, 'error_page.html', {'error_message': 'ログインが必要です'})
    

        
#予算設定画面
@login_required
def set_budget(request):
    now = datetime.now()

    # event_date に現在の日時を使用してフィルタリング
    budgets = Budget.objects.filter(user=request.user, event_date__month=now.month, event_date__year=now.year)

    if budgets.exists():
        # 複数のオブジェクトがある場合は最初のオブジェクトを使用
        budget = budgets.first()
    else:
        # 該当するオブジェクトが存在しない場合は新規作成
        budget = Budget.objects.create(user=request.user, event_date=now)

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('accounts:user')
    else:
        form = BudgetForm(instance=budget)

    return render(request, 'household_budget/set_budget.html', {'form': form, 'current_budget': budget})


#予算表示画面
class BudgetList(ListView):
    template_name = 'budget_list.html'
    model = Budget 
    context_object_name = 'budget_list'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    #今月の表示
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = datetime.now()
        
         # 今月の収支データを取得し、コンテキストに追加
        monthly_totals = self.get_monthly_totals()
        context['monthly_totals'] = monthly_totals
        
        return context
        
 
    # 今月の収支データを取得するメソッド
    def get_monthly_totals(self):
        user = self.request.user
        today = datetime.now().date()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = today.replace(day=28) + timedelta(days=4)
        last_day_of_month = last_day_of_month - timedelta(days=last_day_of_month.day)
        
        monthly_data = Transaction.objects.filter(user=user, event_date__range=[first_day_of_month, last_day_of_month])
        
        monthly_totals = {
            'rent': monthly_data.aggregate(Sum('rent'))['rent__sum'] or 0,
            'water_supply': monthly_data.aggregate(Sum('water_supply'))['water_supply__sum'] or 0,
            'gas': monthly_data.aggregate(Sum('gas'))['gas__sum'] or 0,
            'electricity': monthly_data.aggregate(Sum('electricity'))['electricity__sum'] or 0,
            'food_expenses': monthly_data.aggregate(Sum('food_expenses'))['food_expenses__sum'] or 0,
            'communication_expenses': monthly_data.aggregate(Sum('communication_expenses'))['communication_expenses__sum'] or 0,
            'transportation_expenses': monthly_data.aggregate(Sum('transportation_expenses'))['transportation_expenses__sum'] or 0,
            'insurance_fee': monthly_data.aggregate(Sum('insurance_fee'))['insurance_fee__sum'] or 0,
            'daily_necessities': monthly_data.aggregate(Sum('daily_necessities'))['daily_necessities__sum'] or 0,
            'medical_bills': monthly_data.aggregate(Sum('medical_bills'))['medical_bills__sum'] or 0,
            'entertainment_expenses': monthly_data.aggregate(Sum('entertainment_expenses'))['entertainment_expenses__sum'] or 0,
            'saving': monthly_data.aggregate(Sum('saving'))['saving__sum'] or 0,
            'add_item': monthly_data.aggregate(Sum('add_item'))['add_item__sum'] or 0,
        }
        
        return monthly_totals


# 今月のデータ編集
class BalanceEditView(View):
    template_name = 'edit.html'
    form_class = TransactionForm

    def get(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            balance_entry = Transaction.objects.get(pk=pk) if pk else None
            initial_data = {'name_1': balance_entry.name_1, 'name_2': balance_entry.name_2} if balance_entry else {}
            form = self.form_class(user=request.user, instance=balance_entry, initial=initial_data)
            return render(request, self.template_name, {'form': form, 'balance_entry': balance_entry})
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request, pk=None, *args, **kwargs):
        balance_entry = Transaction.objects.get(pk=pk) if pk else None
        form = self.form_class(request.user, request.POST, instance=balance_entry)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('household_budget:balance')
        else:
            return render(request, self.template_name, {'form': form, 'balance_entry': balance_entry})    
                             
                  
#今月の削除画面
class BalanceDeleteView(View):
    template_name = 'b_delete.html'
    
    def get(self, request, pk, *args, **kwargs):
        balance_entry = get_object_or_404(Transaction, pk=pk, user=request.user)
        return render(request, self.template_name, {'balance_entry': balance_entry})

    def post(self, request, pk, *args, **kwargs):
        balance_entry = get_object_or_404(Transaction, pk=pk, user=request.user)
        balance_entry.delete()
        return HttpResponseRedirect(reverse('household_budget:balance'))

    

#収支画面(ログインが必要)
class TransactionView(ListView):
    template_name = 'balance.html'
    model = Transaction
    context_object_name = 'balance_list'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    #今月の表示
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = datetime.now()

    # 先月のデータを取得
        last_month = datetime.now() - timedelta(days=datetime.now().day)
        context['last_month'] = last_month
        
        return context
    

#貯金画面(ログインが必要)
@method_decorator(login_required, name='dispatch')
class SavingListView(ListView):
    template_name = 'savings.html'
    model = Transaction

    def get_queryset(self):
        # ユーザーごとに月ごとの貯金額を集計する
        return Transaction.objects.filter(user=self.request.user).values('event_date__year', 'event_date__month').annotate(total_savings=Sum('saving'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        monthly_savings = self.get_queryset()
        context['monthly_savings'] = monthly_savings

        total_savings = monthly_savings.aggregate(total_savings=Sum('saving'))['total_savings']
        context['total_savings'] = total_savings if total_savings is not None else 0
        
        # 最新の貯金目標を取得
        latest_goal = Goal_Saving.objects.filter(user=user).order_by('-timestamp').first()
        context['latest_goal'] = latest_goal

        return context


#貯金目標登録
@login_required
def set_goal(request):
    if request.method == 'POST':
        form = SavingForm(request.POST)
        if form.is_valid():
            monthly_goal = form.save(commit=False)
            monthly_goal.user = request.user
            monthly_goal.save()
            return redirect('household_budget:savings')
    else:
        form = SavingForm()

    return render(request, 'goal_savings.html', {'form': form})



#目標リセット
def reset_goal(request):
    try:
        latest_goal_saving = Goal_Saving.objects.latest('timestamp')
        latest_goal_saving.savings_goal = None
        latest_goal_saving.save()
        return redirect('household_budget:savings')
    except Goal_Saving.DoesNotExist:
        # Goal_Saving レコードが存在しない場合の処理
        return redirect('household_budget:savings')

    
#収支データ
class M_DataView(View):
    template_name = 'm_data.html'

    def get(self, request, *args, **kwargs):
        requested_year = kwargs.get('year')
        requested_month = kwargs.get('month')

        if requested_year is not None and requested_month is not None:
            requested_year_month_str = f"{requested_year}-{requested_month}"
        else:
            return HttpResponse('Invalid URL format')

        try:
            requested_year_month = datetime.strptime(requested_year_month_str, "%Y-%m")
        except ValueError:
            return HttpResponse('Invalid date format')

        user = request.user

        # 最新の予算データを取得
        latest_budget = self.get_latest_budget(user, requested_year_month)

        # 各項目の合計を計算
        item_totals = self.calculate_item_totals(user, requested_year_month)

        # 指定された月のデータを取得
        monthly_data = Transaction.objects.filter(
            user=user,
            event_date__year=requested_year_month.year,
            event_date__month=requested_year_month.month,
        )

        context = {
            'monthly_data': monthly_data,
            'requested_year_month': requested_year_month,
            'latest_budget': latest_budget,
            'item_totals': item_totals,
        }

        return render(request, self.template_name, context)

    def get_latest_budget(self, user, requested_year_month):
    # 指定された月の予算データを取得
        latest_budget_queryset = Budget.objects.filter(
        user=user,
        event_date__year=requested_year_month.year,
        event_date__month=requested_year_month.month,
    ).order_by('-event_date')

        if latest_budget_queryset.exists():
           return latest_budget_queryset.first()

    # 指定された月の予算データがない場合は、ユーザーの最も最近のデータを利用
        return Budget.objects.filter(user=user).order_by('-event_date').first()


    def calculate_item_totals(self, user, requested_year_month):
        # 指定された月の各項目の合計を計算
        monthly_data = Transaction.objects.filter(
            user=user,
            event_date__year=requested_year_month.year,
            event_date__month=requested_year_month.month,
        )
             

        item_totals = {
            'rent': monthly_data.aggregate(Sum('rent'))['rent__sum'] or 0,
            'water_supply': monthly_data.aggregate(Sum('water_supply'))['water_supply__sum'] or 0,
            'gas': monthly_data.aggregate(Sum('gas'))['gas__sum'] or 0,
            'electricity': monthly_data.aggregate(Sum('electricity'))['electricity__sum'] or 0,
            'food_expenses': monthly_data.aggregate(Sum('food_expenses'))['food_expenses__sum'] or 0,
            'communication_expenses': monthly_data.aggregate(Sum('communication_expenses'))['communication_expenses__sum'] or 0,
            'transportation_expenses': monthly_data.aggregate(Sum('transportation_expenses'))['transportation_expenses__sum'] or 0,
            'insurance_fee': monthly_data.aggregate(Sum('insurance_fee'))['insurance_fee__sum'] or 0,
            'daily_necessities': monthly_data.aggregate(Sum('daily_necessities'))['daily_necessities__sum'] or 0,
            'medical_bills': monthly_data.aggregate(Sum('medical_bills'))['medical_bills__sum'] or 0,
            'entertainment_expenses': monthly_data.aggregate(Sum('entertainment_expenses'))['entertainment_expenses__sum'] or 0,
            'saving': monthly_data.aggregate(Sum('saving'))['saving__sum'] or 0,
            'add_item': monthly_data.aggregate(Sum('add_item'))['add_item__sum'] or 0,
        }
        
        return item_totals


#前月比
class MonthlyComparisonView(View):
    def get(self, request, year, month):
        user = request.user
        month_comparison = self.calculate_monthly_comparison(user, int(year), int(month))

        context = {
            'month_comparison': month_comparison,
            'year': year,
            'month': month,
        }

        return render(request, 'm_comparison.html', context)

    def calculate_monthly_comparison(self, user, year, month):
        current_month_data = self.get_month_data(user, year, month)

        if month == 1:
            last_month_data = self.get_month_data(user, year - 1, 12)
        else:
            last_month_data = self.get_month_data(user, year, month - 1)

        # 各項目ごとの差分を計算
        month_comparison = {
            'year': year,
            'month': month,
            'total_income_diff': (current_month_data['total_income'] or 0) - (last_month_data['total_income'] or 0),
            'total_rent_diff': (current_month_data['total_rent'] or 0) - (last_month_data['total_rent'] or 0),
            'total_water_supply_diff': (current_month_data['total_water_supply'] or 0) - (last_month_data['total_water_supply'] or 0),
            'total_gas_diff': (current_month_data['total_gas'] or 0) - (last_month_data['total_gas'] or 0),
            'total_electricity_diff': (current_month_data['total_electricity'] or 0) - (last_month_data['total_electricity'] or 0),
            'total_food_expenses_diff': (current_month_data['total_food_expenses'] or 0) - (last_month_data['total_food_expenses'] or 0),
            'total_communication_expenses_diff': (current_month_data['total_communication_expenses'] or 0) - (last_month_data['total_communication_expenses'] or 0),
            'total_transportation_expenses_diff': (current_month_data['total_transportation_expenses'] or 0) - (last_month_data['total_transportation_expenses'] or 0),
            'total_insurance_fee_diff': (current_month_data['total_insurance_fee'] or 0) - (last_month_data['total_insurance_fee'] or 0),
            'total_daily_necessities_diff': (current_month_data['total_daily_necessities'] or 0) - (last_month_data['total_daily_necessities'] or 0),
            'total_medical_bills_diff': (current_month_data['total_medical_bills'] or 0) - (last_month_data['total_medical_bills'] or 0),
            'total_entertainment_expenses_diff': (current_month_data['total_entertainment_expenses'] or 0) - (last_month_data['total_entertainment_expenses'] or 0),
            'total_saving_diff': (current_month_data['total_saving'] or 0) - (last_month_data['total_saving'] or 0),
            'total_add_item_diff': (current_month_data['total_add_item'] or 0) - (last_month_data['total_add_item'] or 0),
            
            'total_fixed_expenses_diff': (
                (current_month_data['total_rent'] or 0) +
                (current_month_data['total_insurance_fee'] or 0) 
            ) - (
                (last_month_data['total_rent'] or 0) +
                (last_month_data['total_insurance_fee'] or 0) 
            ),
            
            'total_utility_costs_diff': (
                (current_month_data['total_water_supply'] or 0) +
                (current_month_data['total_gas'] or 0) +
                (current_month_data['total_electricity'] or 0)
            ) - (
                (last_month_data['total_water_supply'] or 0) +
                (last_month_data['total_gas'] or 0) +
                (last_month_data['total_electricity'] or 0)
            )
        }

        return month_comparison  

    def get_month_data(self, user, year, month):
        # URLから受け取った年と月を元にデータを取得
        current_month_data = Transaction.objects.filter(
            user=user,
            event_date__year=year,
            event_date__month=month
        ).aggregate(
            total_income=Sum('income'),
            total_rent=Sum('rent'),
            total_water_supply=Sum('water_supply'),
            total_gas=Sum('gas'),
            total_electricity=Sum('electricity'),
            total_food_expenses=Sum('food_expenses'),
            total_communication_expenses=Sum('communication_expenses'),
            total_transportation_expenses=Sum('transportation_expenses'),
            total_insurance_fee=Sum('insurance_fee'),
            total_daily_necessities=Sum('daily_necessities'),
            total_medical_bills=Sum('medical_bills'),
            total_entertainment_expenses=Sum('entertainment_expenses'),
            total_saving=Sum('saving'),
            total_add_item=Sum('add_item'),
        )

        last_month_data = Transaction.objects.filter(
            user=user,
            event_date__year=year,
            event_date__month=month - 1 if month > 1 else 12,
        ).aggregate(
            total_income=Sum('income'),
            total_rent=Sum('rent'),
            total_water_supply=Sum('water_supply'),
            total_gas=Sum('gas'),
            total_electricity=Sum('electricity'),
            total_food_expenses=Sum('food_expenses'),
            total_communication_expenses=Sum('communication_expenses'),
            total_transportation_expenses=Sum('transportation_expenses'),
            total_insurance_fee=Sum('insurance_fee'),
            total_daily_necessities=Sum('daily_necessities'),
            total_medical_bills=Sum('medical_bills'),
            total_entertainment_expenses=Sum('entertainment_expenses'),
            total_saving=Sum('saving'),
            total_add_item=Sum('add_item'),
        )

        # 各項目ごとの差分を計算
        month_data = {
            'total_income': (current_month_data['total_income'] or 0),
            'total_rent': (current_month_data['total_rent'] or 0),
            'total_water_supply': (current_month_data['total_water_supply'] or 0),
            'total_gas': (current_month_data['total_gas'] or 0),
            'total_electricity': (current_month_data['total_electricity'] or 0),
            'total_food_expenses': (current_month_data['total_food_expenses'] or 0),
            'total_communication_expenses': (current_month_data['total_communication_expenses'] or 0),
            'total_transportation_expenses': (current_month_data['total_transportation_expenses'] or 0),
            'total_insurance_fee': (current_month_data['total_insurance_fee'] or 0),
            'total_daily_necessities': (current_month_data['total_daily_necessities'] or 0),
            'total_medical_bills': (current_month_data['total_medical_bills'] or 0),
            'total_entertainment_expenses': (current_month_data['total_entertainment_expenses'] or 0),
            'total_saving': (current_month_data['total_saving'] or 0),
            'total_add_item': (current_month_data['total_add_item'] or 0),
        }

        if month != 1:
            # 1月以外の場合、前月のデータも追加
            month_data.update({
                'total_income_last_month': (last_month_data['total_income'] or 0),
                'total_rent_last_month': (last_month_data['total_rent'] or 0),
                'total_water_supply_last_month': (last_month_data['total_water_supply'] or 0),
                'total_gas_last_month': (last_month_data['total_gas'] or 0),
                'total_electricity_last_month': (last_month_data['total_electricity'] or 0),
                'total_food_expenses_last_month': (last_month_data['total_food_expenses'] or 0),
                'total_communication_expenses_last_month': (last_month_data['total_communication_expenses'] or 0),
                'total_transportation_expenses_last_month': (last_month_data['total_transportation_expenses'] or 0),
                'total_insurance_fee_last_month': (last_month_data['total_insurance_fee'] or 0),
                'total_daily_necessities_last_month': (last_month_data['total_daily_necessities'] or 0),
                'total_medical_bills_last_month': (last_month_data['total_medical_bills'] or 0),
                'total_entertainment_expenses_last_month': (last_month_data['total_entertainment_expenses'] or 0),
                'total_saving_last_month': (last_month_data['total_saving'] or 0),
                'total_add_item_last_month': (last_month_data['total_add_item'] or 0),
            })

        return month_data
    