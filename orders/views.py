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
    environment="sandbox"  # change to "production" when you’re ready
)


class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, 'orders/order_form.html', {'form': form})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, 'orders/order_form.html', {'form': form})

        # save the order to get an ID
        order = form.save(commit=False)
        order.save()

        # build the payment‐link body
        idempotency_key = str(uuid.uuid4())
        body = {
            "idempotency_key": idempotency_key,
            "quick_pay": {
                "name": f"Honeybee Order #{order.id}",
                "price_money": {"amount": 1000, "currency": "USD"},
                "location_id": settings.SQUARE_LOCATION_ID,
            }
        }

        # call the Payment Links API
        response = sq_client.payment_links.create_payment_link(body)

        if response.is_success():
            link = response.body['payment_link']
            order.checkout_id = link['id']
            order.save()
            return redirect(link['url'])
        else:
            # show any errors back in the form
            return render(request, 'orders/order_form.html', {
                'form': form,
                'errors': response.errors
            })


def success(request):
    return render(request, 'orders/order_success.html')


def cancel(request):
    return render(request, 'orders/order_cancel.html')
