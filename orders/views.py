import uuid
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

from square.client import Client
from square.environment import SquareEnvironment

from .forms import OrderForm
from .models import Order

# Initialize Square client using the proper class and keyword
sq_client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment=SquareEnvironment.SANDBOX,
)


class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, "orders/order_form.html", {"form": form})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, "orders/order_form.html", {"form": form})

        # Save the Order instance (without committing, so we get an id after save below)
        order = form.save(commit=False)

        # Build your line items (amounts in cents)
        line_items = [
            {
                "name": f"Honeybee Order #{order.id or 'new'}",
                "quantity": "1",
                "base_price_money": {"amount": 1000, "currency": "USD"},
            }
        ]

        body = {
            "idempotency_key": str(uuid.uuid4()),
            "order": {
                "location_id": settings.SQUARE_LOCATION_ID,
                "line_items": line_items,
            },
            "ask_for_shipping_address": False,
            # Where Square should send the customer after they pay:
            "redirect_url": request.build_absolute_uri("/success/"),
        }

        resp = sq_client.checkout.create_checkout(
            location_id=settings.SQUARE_LOCATION_ID,
            body=body,
        )

        if resp.is_success():
            checkout = resp.body["checkout"]
            order.checkout_id = checkout["id"]
            order.save()
            return redirect(checkout["checkout_page_url"])

        # On error, pass the errors list into your template
        return render(
            request,
            "orders/order_form.html",
            {"form": form, "errors": resp.errors},
        )


def success(request):
    return render(request, "orders/order_success.html")


def cancel(request):
    return render(request, "orders/order_cancel.html")
