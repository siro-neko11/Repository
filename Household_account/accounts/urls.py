from django.urls import path
from .views import(
    RegistUserView, UserLoginView, HomeView,
    UserLogoutView, UserDeleteView, UserView,
    Data_2023View, Data_2024View,
)

app_name = 'accounts'
urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('delete/', UserDeleteView.as_view(), name='delete'),
    path('user/', UserView.as_view(), name='user'),
    path('data_2023/', Data_2023View.as_view(), name='data_2023'),
    path('data_2024/', Data_2024View.as_view(), name='data_2024'),
]