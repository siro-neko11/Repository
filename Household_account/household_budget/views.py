from typing import Any
from django.http import HttpRequest
from django.shortcuts import render,redirect
from django.db.models import Sum, Q, Count, Value
from household_budget.models import Transaction, Budget, Goal_Saving, Vendor, Category
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm, SavingForm, BudgetForm, VendorForm
from django.utils.decorators import method_decorator
from django.views.generic.base import  View
from django.http.response import HttpResponse as HttpResponse
from datetime import datetime, timedelta
from django.views.generic import TemplateView
from django.db.models.functions import TruncMonth, Coalesce
from django.utils import timezone
import math




# 収支登録画面
class TransactionRegistView(View):
    template_name = 'b_regist.html'
    form_class = TransactionForm

    def get(self, request, *args, **kwargs):
        transactions = Transaction.objects.all()
        form = self.form_class(user=request.user) 
        vendors = Vendor.objects.filter(user=request.user)
        form.fields['vendor_name'].queryset = vendors
        return render(request, self.template_name, {'transactions': transactions, 'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(user=request.user, data=request.POST)
        if form.is_valid():
            # name_1またはname_2がどちらも入力されていない場合、エラーメッセージを表示
            if not form.cleaned_data['name_1'] and not form.cleaned_data['name_2']:
                form.add_error(None, "本人名またはパートナー名のどちらか一方は入力してください。")
                transactions = Transaction.objects.all()
                return render(request, self.template_name, {'transactions': transactions, 'form': form})

            form.instance.user = request.user
            vendor_name = form.cleaned_data['vendor_name']
            vendor, created = Vendor.objects.get_or_create(vendor_name=vendor_name, user=request.user)
            form.instance.vendor_name = vendor
            form.save()
            return redirect('accounts:user') 
        else:
            transactions = Transaction.objects.all()
            return render(request, self.template_name, {'transactions': transactions, 'form': form})
            

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
            vendor_name = form.cleaned_data['vendor_name']
            user = request.user
            Vendor.objects.create(user=user, vendor_name=vendor_name)
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
            return render(request, 'accounts:login.html')
        
    

        
#予算設定画面
@login_required
def set_budget(request):
    now = datetime.now()

    # event_date に現在の年月を使用してフィルタリング
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


#今月のデータ変更
class UpdateTransactionView(View):
    template_name = 'edit_transaction.html'
    form_class = TransactionForm
    
    def get(self, request, pk, *args, **kwargs):
        transaction_data = Transaction.objects.get(pk=pk)
        form = self.form_class(user=request.user, instance=transaction_data)
        return render(request, self.template_name, {'form': form, 'transaction_data': transaction_data})
    
    def post(self, request, pk, *args, **kwargs):
        transaction_data = Transaction.objects.get(pk=pk)
        form = self.form_class(request.user, request.POST, instance=transaction_data)
        if form.is_valid():
            form.save()
            return redirect('household_budget:balance')
        return render(request, self.template_name, {'form': form, 'transaction_data': transaction_data})
    

#今月のデータ削除
class DeleteTransactionView(View):
    template_name = 'delete_transaction.html'
    form_class = TransactionForm
    
    def get(self, request, pk, *args, **kwargs):
        transaction_data = Transaction.objects.get(pk=pk)
        return render(request, self.template_name, {'transaction_data': transaction_data})
    
    def post(self, request, pk, *args, **kwargs):
        transaction_data = Transaction.objects.get(pk=pk)
        transaction_data.delete()
        return redirect('household_budget:balance')



#今月のデータ
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class TransactionView(TemplateView):
    template_name = 'balance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #ユーザーに関連するデータのみ取得する
        user_transactions = Transaction.objects.filter(user=self.request.user)

        # 今月の最初の日と最後の日を取得
        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = today.replace(day=1, month=today.month+1) - timezone.timedelta(days=1)

        # カテゴリーごとに今月のデータを集計
        category_totals = user_transactions.filter(
            event_date__range=[first_day_of_month, last_day_of_month]
        ).values('category__category_name').annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id')
        )

        # 今月のデータを全て取得
        monthly_transactions = user_transactions.filter(
            event_date__range=[first_day_of_month, last_day_of_month]
        )
        
        # name_1だけに値が入っていた場合の今月の合計
        name1_only_monthly_amount = user_transactions.filter(
            Q(name_1__isnull=False) & ~Q(name_1=''),
            ~Q(category_id=1) & ~Q(category_id=13),
            event_date__range=[first_day_of_month, last_day_of_month]
        ).aggregate(name1_has_data_total_amount=Sum('amount'))['name1_has_data_total_amount'] or 0


        # name_2だけに値が入っていた場合の今月の合計
        name2_only_monthly_amount = user_transactions.filter(
            Q(name_2__isnull=False) & ~Q(name_2=''),
            ~Q(category_id=1) & ~Q(category_id=13),
            event_date__range=[first_day_of_month, last_day_of_month]
        ).aggregate(name1_has_data_total_amount=Sum('amount'))['name1_has_data_total_amount'] or 0
        
        
        
        # 両方に値が入っていた場合の今月の合計
        name_monthly_amount = user_transactions.filter(
            Q(name_1__isnull=False) & Q(name_2__isnull=False) & ~Q(name_1='') & ~Q(name_2=''),
            ~Q(category_id=1) & ~Q(category_id=13),
            event_date__range=[first_day_of_month, last_day_of_month]
        ).aggregate(name_both_total_amount=Sum('amount'))['name_both_total_amount'] or 0

        
        #両方に値が入っていた場合の合計を半分にする
        name_both_half_monthly_amount = math.ceil(name_monthly_amount / 2)
        
        
        # データが無い場合は0を表示させる
        category_totals_dict = {category_name: {'total_amount': 0, 'transaction_count': 0} for category_name in Category.objects.values_list('category_name', flat=True)}

        for category in category_totals:
            category_name = category['category__category_name']
            category_totals_dict[category_name] = {
                'total_amount': category['total_amount'],
                'transaction_count': category['transaction_count']
            }
            
        #mame_1の合計
        name1_total_amount =name1_only_monthly_amount - name_monthly_amount + name_both_half_monthly_amount
        
        #name_2の合計
        name2_total_amount =name2_only_monthly_amount - name_monthly_amount + name_both_half_monthly_amount
        
        context['category_totals'] = category_totals_dict
        context['monthly_transactions'] = monthly_transactions
        context['name1_total_amount'] = name1_total_amount
        context['name2_total_amount'] = name2_total_amount

        return context
    

# 貯金画面(ログインが必要)
@method_decorator(login_required, name='dispatch')
class SavingListView(TemplateView):
    template_name = 'savings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ログインユーザーのIDを取得
        user_id = self.request.user.pk

        # categoryのIDが13でフィルタリング
        transactions_category_13 = Transaction.objects.filter(user_id=user_id, category_id=13)

        # 月ごとの合計金額を計算
        monthly_summary = transactions_category_13.annotate(month=TruncMonth('event_date')).values('month').annotate(total_amount=Sum('amount'))

        # 総合計金額を計算
        total_amount = transactions_category_13.aggregate(total_amount=Sum('amount'))['total_amount']

        # 最新の貯金目標を取得
        latest_savings_goal = Goal_Saving.objects.filter(user_id=user_id, savings_goal__isnull=False).order_by('-timestamp').first()

        context['monthly_summary'] = monthly_summary
        context['total_amount'] = total_amount
        context['latest_savings_goal'] = latest_savings_goal

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
        # ユーザーごとに最新の目標を取得する
        latest_goal_saving = Goal_Saving.objects.filter(user=request.user).latest('timestamp')
        latest_goal_saving.delete()
        return redirect('household_budget:savings')
    except Goal_Saving.DoesNotExist:
        # 目標が存在しない場合のエラーハンドリング
        return redirect('household_budget:savings')


# 各月の収支データ(2023)
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class M_2023DataView(TemplateView):
    template_name = 'm_data.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        # 月初と月末の日付を取得
        first_day_of_month = timezone.datetime(int(year), int(month), 1)
        last_day_of_month = first_day_of_month.replace(day=1, month=first_day_of_month.month + 1) - timezone.timedelta(days=1)

        # 月ごとの集計データを取得
        monthly_summary = Transaction.objects.filter(
            user=self.request.user,
            event_date__year=year,
            event_date__month=month
        ).values('category__category_name') \
            .annotate(total_amount=Coalesce(Sum('amount'), Value(0)))

        # カテゴリ一覧の取得
        categories = ['家賃', '水道代', 'ガス代', '電気代', '食費', '通信費', '交通費', '保険代', '日用品', '医療費', '交際費', '貯金', 'その他']

        # カテゴリごとの合計を取得
        monthly_summary = Transaction.objects.filter(
            user=self.request.user,
            event_date__year=year,
            event_date__month=month
        ).values('category__category_name') \
            .annotate(total_amount=Sum('amount'))
        
        #Transactionからデータ取得
        transaction_data = Transaction.objects.filter(user=self.request.user)

        # name_1だけに値が入っていた場合の今月の合計
        name1_only_monthly_amount = Transaction.objects.filter(
            Q(user=self.request.user) &
            Q(name_1__isnull=False) & ~Q(name_1=''),
            ~Q(category_id=1) & ~Q(category_id=13),
            event_date__range=[first_day_of_month, last_day_of_month]
        ).aggregate(name1_has_data_total_amount=Sum('amount'))['name1_has_data_total_amount'] or 0

        # name_2だけに値が入っていた場合の今月の合計
        name2_only_monthly_amount = Transaction.objects.filter(
            Q(user=self.request.user) &
            Q(name_2__isnull=False) & ~Q(name_2=''),
            ~Q(category_id=1) & ~Q(category_id=13),
            event_date__range=[first_day_of_month, last_day_of_month]
        ).aggregate(name1_has_data_total_amount=Sum('amount'))['name1_has_data_total_amount'] or 0

        # 両方に値が入っていた場合の今月の合計
        name_monthly_amount = Transaction.objects.filter(
            Q(user=self.request.user) &
            Q(name_1__isnull=False) & Q(name_2__isnull=False) & ~Q(name_1='') & ~Q(name_2=''),
            ~Q(category_id=1) & ~Q(category_id=13),
            event_date__range=[first_day_of_month, last_day_of_month]
        ).aggregate(name_both_total_amount=Sum('amount'))['name_both_total_amount'] or 0

        # 両方に値が入っていた場合の合計を半分にする
        name_both_half_monthly_amount = math.ceil(name_monthly_amount / 2)

        # データが無い場合は0を表示させる
        category_totals_dict = {category_name: {'total_amount': 0} for category_name in categories}

        for category in monthly_summary:
            category_name = category['category__category_name']
            category_totals_dict[category_name] = {
                'total_amount': category['total_amount'] if category['total_amount'] is not None else 0
            }

        # 月ごとの詳細データを取得
        monthly_details = Transaction.objects.filter(
            user=self.request.user,
            event_date__year=year,
            event_date__month=month
            )

        # 最新の予算データを取得
        latest_budget = Budget.objects.filter(
            user=self.request.user,
            event_date__year=year,
            event_date__month=month
            ).order_by('-event_date').first()

        # mame_1の合計
        name1_total_amount = name1_only_monthly_amount - name_monthly_amount + name_both_half_monthly_amount

        # name_2の合計
        name2_total_amount = name2_only_monthly_amount - name_monthly_amount + name_both_half_monthly_amount

        context['year'] = year
        context['month'] = month
        context['category_totals'] = category_totals_dict
        context['monthly_details'] = monthly_details
        context['latest_budget'] = latest_budget
        context['name1_total_amount'] = name1_total_amount
        context['name2_total_amount'] = name2_total_amount
        context['name'] = transaction_data

        return context


# 各月の収支データ(2024)
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class M_DataView(TemplateView):
    template_name = 'm_data.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        # 月初と月末の日付を取得
        first_day_of_month = timezone.datetime(int(year), int(month), 1)
        last_day_of_month = first_day_of_month.replace(day=1, month=first_day_of_month.month + 1) - timezone.timedelta(days=1)

        # 月ごとの集計データを取得
        monthly_summary = Transaction.objects.filter(
            user=self.request.user,
            event_date__year=year,
            event_date__month=month
        ).values('category__category_name') \
            .annotate(total_amount=Coalesce(Sum('amount'), Value(0)))

        # カテゴリ一覧の取得
        categories = ['家賃', '水道代', 'ガス代', '電気代', '食費', '通信費', '交通費', '保険代', '日用品', '医療費', '交際費', '貯金', 'その他']

        # カテゴリごとの合計を取得
        monthly_summary = Transaction.objects.filter(
            user=self.request.user,
            event_date__year=year,
            event_date__month=month
        ).values('category__category_name') \
            .annotate(total_amount=Sum('amount'))
        
        #Transactionからデータ取得
        transaction_data = Transaction.objects.filter(user=self.request.user)

        # name_1だけに値が入っていた場合の今月の合計
        name1_only_monthly_amount = Transaction.objects.filter(
            Q(user=self.request.user) &
            Q(name_1__isnull=False) & ~Q(name_1=''),
            ~Q(category_id=1) & ~Q(category_id=13),
            event_date__range=[first_day_of_month, last_day_of_month]
        ).aggregate(name1_has_data_total_amount=Sum('amount'))['name1_has_data_total_amount'] or 0

        # name_2だけに値が入っていた場合の今月の合計
        name2_only_monthly_amount = Transaction.objects.filter(
            Q(user=self.request.user) &
            Q(name_2__isnull=False) & ~Q(name_2=''),
            ~Q(category_id=1) & ~Q(category_id=13),
            event_date__range=[first_day_of_month, last_day_of_month]
        ).aggregate(name1_has_data_total_amount=Sum('amount'))['name1_has_data_total_amount'] or 0

        # 両方に値が入っていた場合の今月の合計
        name_monthly_amount = Transaction.objects.filter(
            Q(user=self.request.user) &
            Q(name_1__isnull=False) & Q(name_2__isnull=False) & ~Q(name_1='') & ~Q(name_2=''),
            ~Q(category_id=1) & ~Q(category_id=13),
            event_date__range=[first_day_of_month, last_day_of_month]
        ).aggregate(name_both_total_amount=Sum('amount'))['name_both_total_amount'] or 0

        # 両方に値が入っていた場合の合計を半分にする
        name_both_half_monthly_amount = math.ceil(name_monthly_amount / 2)

        # データが無い場合は0を表示させる
        category_totals_dict = {category_name: {'total_amount': 0} for category_name in categories}

        for category in monthly_summary:
            category_name = category['category__category_name']
            category_totals_dict[category_name] = {
                'total_amount': category['total_amount'] if category['total_amount'] is not None else 0
            }

        # 月ごとの詳細データを取得
        monthly_details = Transaction.objects.filter(
            user=self.request.user,
            event_date__year=year,
            event_date__month=month
            )

        # 最新の予算データを取得
        latest_budget = Budget.objects.filter(
            user=self.request.user,
            event_date__year=year,
            event_date__month=month
            ).order_by('-event_date').first()

        # mame_1の合計
        name1_total_amount = name1_only_monthly_amount - name_monthly_amount + name_both_half_monthly_amount

        # name_2の合計
        name2_total_amount = name2_only_monthly_amount - name_monthly_amount + name_both_half_monthly_amount

        context['year'] = year
        context['month'] = month
        context['category_totals'] = category_totals_dict
        context['monthly_details'] = monthly_details
        context['latest_budget'] = latest_budget
        context['name1_total_amount'] = name1_total_amount
        context['name2_total_amount'] = name2_total_amount
        context['name'] = transaction_data

        return context
    

#前月比(2024)
class MonthlyComparisonView(TemplateView):
    template_name = 'm_comparison.html'
    
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL から年と月を取得
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        # 対象月のデータを取得
        current_month_data = Transaction.objects.filter(user=self.request.user, event_date__year=year, event_date__month=month)

        # 前月のデータを取得
        last_month = datetime(int(year), int(month), 1) - timedelta(days=1)
        last_month_data = Transaction.objects.filter(user=self.request.user, event_date__year=last_month.year, event_date__month=last_month.month)

        # カテゴリごとの合計を計算
        current_month_totals = current_month_data.values('category__category_name').annotate(total_amount=Sum('amount'))
        last_month_totals = last_month_data.values('category__category_name').annotate(total_amount=Sum('amount'))

        # カテゴリの一覧を取得
        categories = Category.objects.all()

        # データを整形してコンテキストに追加
        comparison_data = []
        for category in categories:
            current_amount = next((item['total_amount'] for item in current_month_totals if item['category__category_name'] == category.category_name), 0)
            last_amount = next((item['total_amount'] for item in last_month_totals if item['category__category_name'] == category.category_name), 0)
            comparison_data.append({
                'category': category.category_name,
                'current_amount': current_amount,
                'last_amount': last_amount,
                'percentage_change': last_amount - current_amount
            })

        context['year'] = year
        context['month'] = month
        context['comparison_data'] = comparison_data

        return context
    