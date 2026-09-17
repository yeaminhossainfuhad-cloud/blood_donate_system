from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html', authentication_form=LoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Profile
    path('profile/', views.profile_detail, name='profile-detail'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),

    # Donors
    path('donors/', views.donor_list, name='donor-list'),
    path('donors/<int:pk>/', views.donor_detail, name='donor-detail'),

    # Blood requests
    path('requests/', views.request_list, name='request-list'),
    path('requests/mine/', views.my_requests, name='my-requests'),
    path('requests/create/', views.request_create, name='request-create'),
    path('requests/<int:pk>/', views.request_detail, name='request-detail'),
    path('requests/<int:pk>/edit/', views.request_update, name='request-update'),
    path('requests/<int:pk>/delete/', views.request_delete, name='request-delete'),
]
