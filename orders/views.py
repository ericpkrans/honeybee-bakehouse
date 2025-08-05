# orders/views.py

import uuid
import requests
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

from .forms import OrderForm
from .models import Order

class OrderCreate(View):
    def get(self, request):
        return render(request, 'orders/order_form.html', {'form': OrderForm()})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, 'orders/order_form.html', {'form': form})

        # Save the Order so we have an ID to put in the line item name
        order = form.save(commit=False)
        order.save()

        # Build the Checkout API payload
        checkout_body = {
            "idempotency_key": str(uuid.uuid4()),
            "order": {
                "location_id": settings.SQUARE_LOCATION_ID,
                "line_items": [
                    {
                        "name": f"Honeybee Order #{order.id}",
                        "quantity": "1",
                        "base_price_money": {
                            # 1000 = $10.00
                            "amount": 1000,
                            "currency": "USD"
                        }
                    }
                ]
            },
            "ask_for_shipping_address": False,
            "redirect_url": request.build_absolute_uri('/success/')
        }

        # Call Square Checkout API directly
        url = f'https://connect.squareup.com/v2/locations/{settings.SQUARE_LOCATION_ID}/checkouts'
        headers = {
            'Authorization': f'Bearer {settings.SQUARE_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        resp = requests.post(url, json=checkout_body, headers=headers)

        if resp.status_code == 200:
            data = resp.json().get('checkout', {})
            # Persist the Square checkout id & URL
            order.checkout_id = data.get('id')
            order.payment_link_url = data.get('checkout_page_url')
            order.save()
            # Redirect your customer to the Square-hosted page
            return redirect(order.payment_link_url)

        # On error, show messages to the user
        errors = resp.json().get('errors', [])
        return render(request, 'orders/order_form.html', {
            'form': form,
            'errors': errors
        })


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')
