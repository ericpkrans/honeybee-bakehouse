from django.urls import path
from orders.views import OrderCreate, OrderSuccess

urlpatterns = [
    path("", OrderCreate.as_view(), name="order_create"),
    path("success/", OrderSuccess.as_view(), name="order_success"),
]
