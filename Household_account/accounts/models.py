from django.db import models
from django.contrib.auth.models import(
    BaseUserManager,AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy

# 通常のユーザーを作成
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Enter Email')
        user = self.model(
            username=username,
            email=email            
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    

# ユーザー情報
class User(AbstractBaseUser, PermissionsMixin):
    user_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = UserManager()
    
    def get_absolute_url(self):
        return reverse_lazy('accounts:home')
    
    class Meta:
        db_table = 'user'