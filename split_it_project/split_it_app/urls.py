from django.urls import path, include
from .views import RegisterApi, LoginApi, UserApi, OccasionApi, EventApi, ExpenseApi, OccasionSummaryApi

app_name = 'split_it_app'

urlpatterns = [
    path('register/', RegisterApi.as_view(), name = 'register_users'),
    path('login/', LoginApi.as_view(), name = 'login_users'),
    path('users/', UserApi.as_view(), name = 'get_users'),  
    path('occasion/', OccasionApi.as_view(), name = 'occasion-view-create'),
    path('occasion/<int:pk>/summary', OccasionSummaryApi.as_view(), name = 'occasion-summary'),
    path('event/', EventApi.as_view(), name = 'event-view-create'),
    path('event/clear_expense', ExpenseApi.as_view(), name = 'expense-clear'),
]
