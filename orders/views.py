# orders/views.py

import uuid
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

# NOTE: we’re importing from the squareup package (your requirements.txt)
from square.client import Client
from square.environment import Environment

from .forms import OrderForm
from .models import Order

# Initialize the Square client
sq_client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment=Environment.SANDBOX,  # or Environment.PRODUCTION
)


class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, 'orders/order_form.html', {'form': form})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, 'orders/order_form.html', {'form': form})

        order = form.save(commit=False)

        # Build your line items
        line_items = [{
            "name": f"Honeybee Order #{order.id or 'new'}",
            "quantity": "1",
            "base_price_money": {
                "amount": 1000,    # $10.00
                "currency": "USD"
            }
        }]

        # The body for the Checkout API
        body = {
            "idempotency_key": str(uuid.uuid4()),
            "order": {
                "location_id": settings.SQUARE_LOCATION_ID,
                "line_items": line_items
            },
            "ask_for_shipping_address": False,
            "redirect_url": request.build_absolute_uri('/success/')
        }

        # Use the new `.create()` method on the checkout client
        response = sq_client.checkout.create(
            location_id=settings.SQUARE_LOCATION_ID,
            body=body
        )

        if response.is_success():
            checkout = response.body['checkout']
            order.checkout_id = checkout['id']
            order.checkout_url = checkout['checkout_page_url']
            order.save()
            return redirect(checkout['checkout_page_url'])
        else:
            # surface any Square errors in the form
            return render(request, 'orders/order_form.html', {
                'form': form,
                'errors': response.errors
            })


# simple function-views for success / cancel
def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')
