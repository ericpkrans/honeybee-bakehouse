import uuid
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from square.client import Client
from .forms import OrderForm
from .models import Order

# init the client
sq_client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment="sandbox",
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
        order.save()   # so order.id exists

        # build the Payment Link payload
        body = {
            "idempotency_key": str(uuid.uuid4()),
            "quick_pay": {
                "location_id": settings.SQUARE_LOCATION_ID,
                "name":      f"Honeybee Order #{order.id}",
                "price_money": {
                    "amount":   1000,   # $10.00 in cents
                    "currency": "USD"
                }
            },
            "checkout_options": {
                "ask_for_shipping_address": False,
                "redirect_url": request.build_absolute_uri('/success/')
            },
            "pre_populated_data": {
                "buyer_email": form.cleaned_data['email']
            }
        }

        # call the new Payment Links API
        resp = sq_client.payment_links.create_payment_link(body=body)
        if resp.is_success():
            link = resp.body["payment_link"]["url"]
            link_id = resp.body["payment_link"]["id"]
            order.checkout_id = link_id
            order.payment_link_url = link
            order.save()
            return redirect(link)


        # on error, put errors back into the form
        return render(request, 'orders/order_form.html', {
            'form':   form,
            'errors': response.errors
        })


def success(request):
    return render(request, 'orders/success.html')


def cancel(request):
    return render(request, 'orders/cancel.html')
