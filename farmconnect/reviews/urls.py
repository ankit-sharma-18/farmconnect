from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('farmer/<int:farmer_id>/', views.review_list, name='farmer_reviews'),
    path('create/<int:order_id>/', views.create_review, name='create_review'),
    path('<int:pk>/edit/', views.edit_review, name='edit_review'),
    path('<int:pk>/delete/', views.delete_review, name='delete_review'),
]