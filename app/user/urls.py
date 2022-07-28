from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('me/', views.UserDetailView.as_view(), name='user-detail'),
    path('change-password/', views.UserUpdatePassword.as_view(), name='change-password'),
    path('reset-password/', views.PasswordResetRequestView.as_view(), name='reset-password'),
    path('reset-password/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
]
