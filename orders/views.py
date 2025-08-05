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
    environment="sandbox"  # swap to "production" when you go live
)

class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, 'orders/order_form.html', {'form': form})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, 'orders/order_form.html', {'form': form})

        # save the order so we have an ID
        order = form.save(commit=False)
        order.save()

        # build your payment link request
        body = {
            "idempotency_key": str(uuid.uuid4()),
            "quick_pay": {
                "name": f"Honeybee Order #{order.id}",
                "price_money": {
                    "amount": 1000,     #  $10.00
                    "currency": "USD"
                },
                "location_id": settings.SQUARE_LOCATION_ID
            }
        }

        # call the Payment Links API
        result = sq_client.payment_links.create_payment_link(body)

        if result.is_success():
            link = result.body['payment_link']
            # store the link ID if you want to look it up later
            order.checkout_id = link['id']
            order.save()
            # redirect the customer to Square’s hosted payment page
            return redirect(link['url'])

        # on error, re-render form with any messages
        return render(request, 'orders/order_form.html', {
            'form':   form,
            'errors': result.errors
        })


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')
