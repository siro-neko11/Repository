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
    
    def create_superuser(self, user_name, email, password=None):
        user = self.model(
            user_name=user_name,
            email=email,
        )
        user.set_password(password)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    

# ユーザー情報
class User(AbstractBaseUser, PermissionsMixin):
    user_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    def get_absolute_url(self):
        return reverse_lazy('accounts:home')
    
    class Meta:
        db_table = 'user'