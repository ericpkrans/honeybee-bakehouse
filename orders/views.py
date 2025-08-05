from django.shortcuts import render, redirect
from django.views import View
from .forms import OrderForm

class OrderCreate(View):
    template_name = 'orders/order_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': OrderForm()})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        # simply save the order
        form.save()
        return redirect('orders:success')


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    # you can retire this if you never need it
    return render(request, 'orders/cancel.html')
