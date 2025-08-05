import uuid
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

# New SDK entrypoint
from square import Square
from square.environment import SquareEnvironment

from .forms import OrderForm
from .models import Order

# initialize your Square client
sq_client = Square(
    environment=SquareEnvironment.SANDBOX,          # or PRODUCTION
    token=settings.SQUARE_ACCESS_TOKEN,             # use `token=…` here
)

class OrderCreate(View):
    def get(self, request):
        return render(request, 'orders/order_form.html', {'form': OrderForm()})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, 'orders/order_form.html', {'form': form})

        order = form.save(commit=False)
        order.save()

        checkout_body = {
            "idempotency_key": str(uuid.uuid4()),
            "order": {
                "location_id": settings.SQUARE_LOCATION_ID,
                "line_items": [{
                    "name": f"Honeybee Order #{order.id}",
                    "quantity": "1",
                    "base_price_money": {"amount": 1000, "currency": "USD"}
                }]
            },
            "ask_for_shipping_address": False,
            "redirect_url": request.build_absolute_uri('/success/')
        }

        # <-- use payment_links, not checkout
        response = sq_client.payment_links.create_payment_link(body=checkout_body)

        if response.is_success():
            payment_link = response.body['payment_link']
            order.checkout_id = payment_link['id']
            order.save()
            return redirect(payment_link['url'])

        return render(request, 'orders/order_form.html', {
            'form': form,
            'errors': response.errors
        })

        # ← CALL THE NEW METHOD create_payment_link
        response = sq_client.checkout.create_payment_link(body=checkout_body)

        if response.is_success():
            payment_link = response.body['payment_link']
            order.checkout_id = payment_link['id']
            order.save()
            return redirect(payment_link['url'])

        # on error, render form with errors
        return render(request, 'orders/order_form.html', {
            'form':   form,
            'errors': response.errors
        })

def success(request):
    return render(request, 'orders/success.html')

def cancel(request):
    return render(request, 'orders/cancel.html')
