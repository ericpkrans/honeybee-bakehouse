import uuid
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

from square import Square
from square.environment import SquareEnvironment

from .forms import OrderForm
from .models import Order

# Initialize the Square client
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
        if not form.is_valid():
            return render(request, 'orders/order_form.html', {'form': form})

        order = form.save(commit=False)
        # Build your order payload
        body = {
            "idempotency_key": str(uuid.uuid4()),
            "order": {
                "location_id": settings.SQUARE_LOCATION_ID,
                "line_items": [{
                    "name": f"Honeybee Order #{order.id or 'new'}",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1000,    # in cents, so $10.00
                        "currency": "USD"
                    }
                }]
            },
            "checkout_options": {
                "redirect_url": request.build_absolute_uri('/success/')
            }
        }

        # Create a Payment Link (replaces the old create_checkout)
        response = sq_client.payment_links.create_payment_link(body)

        if response.is_success():
            link = response.body['payment_link']['url']
            order.checkout_url = link  # you may want to store this
            order.save()
            return redirect(link)
        else:
            # Pass any API errors back to the template
            return render(request, 'orders/order_form.html', {
                'form': form,
                'errors': response.errors,
            })

def success(request):
    return render(request, 'orders/order_success.html')

def cancel(request):
    return render(request, 'orders/order_cancel.html')
