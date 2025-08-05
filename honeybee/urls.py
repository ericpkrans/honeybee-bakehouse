from django.contrib import admin
from django.urls import path
from orders.views import OrderCreate, success, cancel

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', OrderCreate.as_view(), name='order-create'),
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
]
