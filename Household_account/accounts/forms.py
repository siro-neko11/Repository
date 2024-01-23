from django import forms
from .models import User
from django.contrib.auth.password_validation import validate_password


#ユーザー登録画面
class RegistForm(forms.ModelForm):
    user_name = forms.CharField(label='名前')
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ['user_name', 'email', 'password']
        
    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user    
    
#ログイン画面
class LoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='ログイン状態を保持する', required=False)
    
