# orders/views.py

import uuid
import requests
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

from .forms import OrderForm
from .models import Order

# Base URL for Square’s REST API
SQUARE_API_BASE = "https://connect.squareup.com"

class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, "orders/order_form.html", {"form": form})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, "orders/order_form.html", {"form": form})

        # Save the order so we have an order.id
        order = form.save(commit=False)
        order.save()

        # Build the Checkout API payload
        body = {
            "idempotency_key": str(uuid.uuid4()),
            "order": {
                "location_id": settings.SQUARE_LOCATION_ID,
                "line_items": [
                    {
                        "name": f"Honeybee Order #{order.id}",
                        "quantity": "1",
                        "base_price_money": {
                            "amount": 1000,     # $10.00 in cents
                            "currency": "USD"
                        }
                    }
                ]
            },
            "ask_for_shipping_address": False,
            "redirect_url": request.build_absolute_uri("/success/")
        }

        headers = {
            "Authorization": f"Bearer {settings.SQUARE_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Call the Checkout API
        url = f"{SQUARE_API_BASE}/v2/locations/{settings.SQUARE_LOCATION_ID}/checkouts"
        resp = requests.post(url, json=body, headers=headers)

        if resp.status_code in (200, 201):
            data = resp.json()
            checkout = data.get("checkout")
            if checkout:
                # Persist the checkout ID and redirect user
                order.checkout_id = checkout.get("id")
                order.save()
                return redirect(checkout.get("checkout_page_url"))

        # On error, pull out any errors returned and show them on the form
        try:
            errors = resp.json().get("errors", [])
        except ValueError:
            errors = [{"detail": "Unable to create checkout link."}]

        return render(request, "orders/order_form.html", {
            "form": form,
            "errors": errors
        })


def success(request):
    return render(request, "orders/success.html")


def cancel(request):
    return render(request, "orders/cancel.html")
