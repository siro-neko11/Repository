from django.shortcuts import render,redirect, get_object_or_404
from django.db.models import Sum
from household_budget.models import Transaction, Budget, Goal_Saving, Vendor, Category
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm, SavingForm, BudgetForm, VendorForm
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.generic.base import  View
from django.http.response import HttpResponse as HttpResponse
from datetime import datetime, timedelta
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponseNotFound
from django.contrib import messages
from django.views.generic import TemplateView, DeleteView, DetailView, UpdateView
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied




# 収支登録画面
class TransactionRegistView(View):
    template_name = 'b_regist.html'
    form_class = TransactionForm

    def get(self, request, *args, **kwargs):
        transactions = Transaction.objects.all()
        form = self.form_class(user=request.user)  # userを渡す
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
            return render(request, 'error_page.html', {'error_message': 'ログインが必要です'})
    

        
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


# 今月のデータ編集
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)

    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')  # 編集後にリダイレクトする先を指定
    else:
        form = TransactionForm(request.user, instance=transaction)

    # テンプレートに渡すデータにURLを追加
    edit_url = reverse('edit_transaction', args=[transaction.pk])
    return render(request, 'edit_transaction.html', {'form': form, 'transaction': transaction, 'edit_url': edit_url})



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
class TransactionView(TemplateView):
    template_name = 'balance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 今月のデータだけを取得
        current_month = timezone.now().replace(day=1)  # 現在の月の1日を取得

        transactions = Transaction.objects.filter(
            user=self.request.user,
            event_date__year=current_month.year,
            event_date__month=current_month.month
        )

        # categoryごとに集計
        monthly_summary = transactions.values('category__category_name').annotate(total_amount=Sum('amount'))
        
        # カテゴリーIDでソート
        sorted_monthly_summary = sorted(
            monthly_summary,
            key=lambda x: x['category__category_name']
        )
        
        context['sorted_monthly_summary'] = sorted_monthly_summary

        # 日付、name1、name2も表示する
        detailed_transactions = transactions.values(
            'event_date', 'name_1', 'name_2', 'category__category_name', 'amount',
            'payment_type__payment_type', 'vendor_name__vendor_name', 'memo')

        context['detailed_transactions'] = detailed_transactions

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
        latest_goal_saving = Goal_Saving.objects.latest('timestamp')
        latest_goal_saving.savings_goal = None
        latest_goal_saving.save()
        return redirect('household_budget:savings')
    except Goal_Saving.DoesNotExist:
        # Goal_Saving レコードが存在しない場合の処理
        return redirect('household_budget:savings')

    
#収支データ
class M_DataView(TemplateView):
    template_name = 'm_data.html'  # 作成するHTMLテンプレートの名前に変更してください

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URLから年と月を取得
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        # 月ごとの集計データを取得
        monthly_summary = Transaction.objects.filter(event_date__year=year, event_date__month=month)\
            .values('category__category_name')\
            .annotate(total_amount=Sum('amount'))
        
        #データが無い場合の処理
        if not monthly_summary:
            context['no_data_message'] = 'データが未入力です'
            return context

        # 月ごとの詳細データを取得
        monthly_details = Transaction.objects.filter(event_date__year=year, event_date__month=month)

        # 最新の予算データを取得
        latest_budget = Budget.objects.filter(event_date__year=year, event_date__month=month).order_by('-event_date').first()


        context['year'] = year
        context['month'] = month
        context['monthly_summary'] = monthly_summary
        context['monthly_details'] = monthly_details
        context['latest_budget'] = latest_budget

        return context
    

#前月比
class MonthlyComparisonView(TemplateView):
    template_name = 'm_comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL から年と月を取得
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        # 対象月のデータを取得
        current_month_data = Transaction.objects.filter(event_date__year=year, event_date__month=month)

        # 前月のデータを取得
        last_month = datetime(year, month, 1) - timedelta(days=1)
        last_month_data = Transaction.objects.filter(event_date__year=last_month.year, event_date__month=last_month.month)

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
    