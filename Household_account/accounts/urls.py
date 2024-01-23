from django.urls import path
from .views import(
    RegistUserView, UserLoginView, HomeView,
    UserLogoutView, UserDeleteView, UserView
)

app_name = 'accounts'
urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('delete/', UserDeleteView.as_view(), name='delete'),
    path('user/', UserView.as_view(), name='user'),
]