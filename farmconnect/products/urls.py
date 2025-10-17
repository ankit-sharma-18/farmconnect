from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('search/', views.search, name='search'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('my-products/', views.farmer_products, name='farmer_products'),
    path('ai-recommendations/', views.ai_recommendations, name='ai_recommendations'),
]