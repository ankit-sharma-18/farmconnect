from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('farmer/<int:pk>/', views.farmer_profile_view, name='farmer_profile'),
    path('buyer/<int:pk>/', views.buyer_profile_view, name='buyer_profile'),
]