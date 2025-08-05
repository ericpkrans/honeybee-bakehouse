import uuid

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings

from square.client import Client

from .forms import OrderForm
from .models import Order

# initialize your Square client
sq_client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment="sandbox"  # change to "production" when you go live
)


class OrderCreate(View):
    def get(self, request):
        form = OrderForm()
        return render(request, 'orders/order_form.html', {'form': form})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, 'orders/order_form.html', {'form': form})

        # save the order so we have an order.id
        order = form.save(commit=False)
        order.save()

        # build the Payment Link payload
        payload = {
            "idempotency_key": str(uuid.uuid4()),
            "quick_pay": {
                "name": f"Honeybee Order #{order.id}",
                "price_money": {
                    "amount": 1000,      # $10.00 in cents
                    "currency": "USD"
                }
            },
            "checkout_options": {
                "redirect_url": request.build_absolute_uri('/success/')
            }
        }

        # create a hosted payment link
        response = sq_client.payment_links.create_payment_link(body=payload)

        if response.is_success():
            link_url = response.body['payment_link']['url']
            # you can store link_url on order if you want:
            # order.checkout_url = link_url; order.save()
            return redirect(link_url)

        # render errors back to the form
        return render(request, 'orders/order_form.html', {
            'form': form,
            'errors': response.errors
        })


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')
