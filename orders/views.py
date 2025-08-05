# orders/views.py

import uuid

from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View

from square.client import Client

from .forms import OrderForm
from .models import Order


class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, 'orders/order_form.html', {'form': form})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, 'orders/order_form.html', {'form': form})

        # save a stub Order so we have an ID to show on the Square page
        order = form.save(commit=False)
        order.save()

        # … after order.save()
        order.checkout_id = 'DEMO'
        order.save()
        return redirect('/success/')


        # initialize Square client
        client = Client(
            access_token=settings.SQUARE_ACCESS_TOKEN,
            environment='sandbox'  # or 'production'
        )

        # build the Payment Link request
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
            "checkout_options": {
                "redirect_url": request.build_absolute_uri('/success/'),
                "ask_for_shipping_address": False
            }
        }

        # call the Payment Links API
        resp = client.payment_links.create_payment_link(body)
        if resp.is_success():
            link = resp.body['payment_link']['url']
            order.checkout_id = resp.body['payment_link']['id']
            order.save()
            return redirect(link)

        # on error, show them back the form with Square’s errors
        return render(request, 'orders/order_form.html', {
            'form': form,
            'errors': resp.errors
        })


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')
