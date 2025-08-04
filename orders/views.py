import uuid

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

from square import Square
from square.environment import SquareEnvironment

from .forms import OrderForm
from .models import Order

# Initialize Square client
sq_client = Square(
    environment=SquareEnvironment.SANDBOX,
    token=settings.SQUARE_ACCESS_TOKEN,
)


class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, 'orders/order_form.html', {'form': form})

    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            # Build a single line item; adjust amount as needed (in cents)
            line_items = [{
                "name": f"Honeybee Order #{order.id or 'new'}",
                "quantity": "1",
                "base_price_money": {
                    "amount": 1000,       # e.g. $10.00
                    "currency": "USD"
                }
            }]

            body = {
                "idempotency_key": str(uuid.uuid4()),
                "order": {
                    "location_id": settings.SQUARE_LOCATION_ID,
                    "line_items": line_items
                },
                "ask_for_shipping_address": False,
                "redirect_url": request.build_absolute_uri('/success/')
            }

            # Create the checkout session
            response = sq_client.checkout.create_checkout(
                location_id=settings.SQUARE_LOCATION_ID,
                body=body
            )

            if response.is_success():
                checkout = response.body['checkout']
                order.checkout_id = checkout['id']
                order.save()
                return redirect(checkout['checkout_page_url'])
            else:
                # Pass Square errors back to template
                errors = response.errors
                return render(request, 'orders/order_form.html', {
                    'form': form,
                    'errors': errors
                })

        return render(request, 'orders/order_form.html', {'form': form})


def success(request):
    return render(request, 'orders/order_success.html')


def cancel(request):
    return render(request, 'orders/order_cancel.html')
