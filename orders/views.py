import uuid

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

from square.client import Client

from .forms import OrderForm
from .models import Order

# Initialize Square client
sq_client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment="sandbox"  # or "production" if you’ve switched your tokens
)

class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, 'orders/order_form.html', {'form': form})

    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            # Save the order (to get an ID for the line item name)
            order = form.save(commit=False)
            order.save()

            line_items = [{
                "name": f"Honeybee Order #{order.id}",
                "quantity": "1",
                "base_price_money": {
                    "amount": 1000,    # $10.00 in cents
                    "currency": "USD"
                }
            }]

            body = {
                "idempotency_key": str(uuid.uuid4()),
                "order": {
                    "location_id": settings.SQUARE_LOCATION_ID,
                    "line_items": line_items,
                },
                "ask_for_shipping_address": False,
                "redirect_url": request.build_absolute_uri('/success/')
            }

            # Create a checkout session
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
                # Show any Square errors
                return render(request, 'orders/order_form.html', {
                    'form': form,
                    'errors': response.errors
                })

        return render(request, 'orders/order_form.html', {'form': form})


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')
