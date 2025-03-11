from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # <= à importer pour processus de réinitialisation de mots de passe
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.signup, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    # path('result/', views.result, name='result'),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('update_profile/', views.updateProfile, name='update-profile'),
    
     path('delete_account/', views.delete_account, name='delete_account'),
    
    # urls pour la réinitialisation du mot de passe
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="api_credit/password_reset.html", form_class=CustomPasswordResetForm), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="api_credit/password_reset_sent.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="api_credit/password_reset_form.html", form_class=CustomSetPasswordForm), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="api_credit/password_reset_done.html"), name='password_reset_complete'),
    
]


