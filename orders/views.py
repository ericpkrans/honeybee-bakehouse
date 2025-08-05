import uuid
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from square.client import Client
from .forms import OrderForm
from .models import Order

# initialize the Square client
sq_client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment="sandbox"  # or "production"
)

class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, "orders/order_form.html", {"form": form})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, "orders/order_form.html", {"form": form})

        order = form.save(commit=False)
        order.save()  # need order.id for the link name

        # build the payment link request
        link_body = {
            "idempotency_key": str(uuid.uuid4()),
            "quick_pay": {
                "name": f"Honeybee Order #{order.id}",
                "price_money": {
                    "amount": 1000,   # $10.00 in cents
                    "currency": "USD"
                },
                "location_id": settings.SQUARE_LOCATION_ID
            },
            "checkout_options": {
                "redirect_url": request.build_absolute_uri("/success/")
            }
        }

        # call the Payment Links API
        response = sq_client.payment_links.create_payment_link(link_body)

        if response.is_success():
            payment_link = response.body["payment_link"]
            order.checkout_id = payment_link["id"]
            order.save()
            return redirect(payment_link["url"])

        # render errors back to the form
        return render(request, "orders/order_form.html", {
            "form": form,
            "errors": response.errors
        })


def success(request):
    return render(request, "orders/success.html")


def cancel(request):
    return render(request, "orders/cancel.html")
