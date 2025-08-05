# orders/views.py

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import OrderForm
from .models import Order

class OrderCreate(FormView):
    template_name = "orders/order_form.html"
    form_class = OrderForm
    success_url = reverse_lazy("order_success")

    def form_valid(self, form):
        # save the Order to the database
        form.save()
        return super().form_valid(form)

class OrderSuccess(TemplateView):
    template_name = "orders/success.html"
