import uuid
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

# use the new Square SDK
from square import Square
from square.environment import SquareEnvironment

from .forms import OrderForm
from .models import Order

# initialize your Square client
sq_client = Square(
    token=settings.SQUARE_ACCESS_TOKEN,
    environment=SquareEnvironment.SANDBOX  # or PRODUCTION when you go live
)

class OrderCreate(View):
    def get(self, request):
        return render(request, 'orders/order_form.html', {'form': OrderForm()})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, 'orders/order_form.html', {'form': form})

        order = form.save(commit=False)
        order.save()  # now order.id exists

        checkout_body = {
            "idempotency_key": str(uuid.uuid4()),
            "order": {
                "location_id": settings.SQUARE_LOCATION_ID,
                "line_items": [{
                    "name": f"Honeybee Order #{order.id}",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1000,    # in cents, so $10.00
                        "currency": "USD"
                    }
                }]
            },
            "ask_for_shipping_address": False,
            "redirect_url": request.build_absolute_uri('/success/')
        }

        # call the Checkout API
        # Note: in the new SDK .checkout is already available
        response = sq_client.checkout.create_checkout(
            location_id=settings.SQUARE_LOCATION_ID,
            body=checkout_body
        )

        if response.is_success():
            checkout = response.body['checkout']
            order.checkout_id = checkout['id']
            order.save()
            return redirect(checkout['checkout_page_url'])

        # on error, re‐render form with errors
        return render(request, 'orders/order_form.html', {
            'form':   form,
            'errors': response.errors
        })

def success(request):
    return render(request, 'orders/success.html')

def cancel(request):
    return render(request, 'orders/cancel.html')
