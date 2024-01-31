from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import TemplateView, View
from django.views.generic import DeleteView
from .forms import RegistForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages


#ホーム画面
class HomeView(TemplateView):
    template_name ='home.html'


#2023年画面
class Data_2023View(TemplateView):
    template_name ='data_2023.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    
#2024年画面
class Data_2024View(TemplateView):
    template_name = 'data_2024.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


    

    
#ユーザー登録
class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm
    
    
#ログイン画面
class UserLoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    
    def form_valid(self, form):
        remember = form.cleaned_data['remember']
        if remember:
            self.request.session.set_expiry(2678400)
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        next_url = request.POST.get('next', '')
        
        if user is not None and user.is_active:
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect('accounts:home')
        else:
            # アカウントが存在しないか無効な場合のエラーメッセージ
            messages.error(request, 'アカウントが存在しないか無効です。')
            return redirect('accounts:login')  # アカウント登録ページにリダイレクト

#ログアウト画面
class UserLogoutView(View):
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:home')


#家計簿画面（ユーザー画面）
class UserView(TemplateView):
    template_name = 'user.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
    
        messages_list = messages.get_messages(self.request)
        self.extra_context = {'messages': messages_list}
        return response
    

#ユーザー情報削除画面
class UserDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'delete.html'
    success_url = reverse_lazy('accounts:home')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            user.delete()
            return redirect(self.success_url)
        else:
            return redirect('accounts:login')