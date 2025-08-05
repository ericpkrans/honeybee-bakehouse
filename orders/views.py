# orders/views.py
import uuid
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from square.client import Client

from .forms import OrderForm
from .models import Order

# initialize the Square client
sq_client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment="sandbox"  # or "production" when you go live
)

class OrderCreate(View):
    template_name = 'orders/order_form.html'

    def get(self, request):
        form = OrderForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        order = form.save(commit=False)
        order.save()  # now order.id is available

        checkout_body = {
            "idempotency_key": str(uuid.uuid4()),
            "order": {
                "location_id": settings.SQUARE_LOCATION_ID,
                "line_items": [{
                    "name": f"Honeybee Order #{order.id}",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1000,    # in cents
                        "currency": "USD"
                    }
                }]
            },
            "ask_for_shipping_address": False,
            "redirect_url": request.build_absolute_uri('/success/')
        }

        response = sq_client.checkout.create_checkout(
            location_id=settings.SQUARE_LOCATION_ID,
            body=checkout_body
        )

        if response.is_success():
            checkout = response.body['checkout']
            order.checkout_id = checkout['id']
            order.save()
            return redirect(checkout['checkout_page_url'])

        return render(request, self.template_name, {
            'form': form,
            'errors': response.errors
        })

def success(request):
    return render(request, 'orders/success.html')

def cancel(request):
    return render(request, 'orders/cancel.html')
