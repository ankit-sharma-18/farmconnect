from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('create/<int:product_id>/', views.create_order, name='create_order'),
    path('<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('messages/', views.messaging, name='messaging'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/send/<int:recipient_id>/', views.send_message, name='send_message_to'),
    path('messages/send/order/<int:order_id>/', views.send_message, name='send_message_order'),
]