from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.OrderCreateView.as_view(), name='orders_create'),
    path('order/<int:order_id>/pdf', views.AdminOrderPDFView.as_view(), name='admin_order_pdf'),
]
