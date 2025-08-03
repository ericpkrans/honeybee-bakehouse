from django.db import models

# Create your models here.
from django.db import models

class Order(models.Model):
    PICKUP = 'P'
    DELIVERY = 'D'
    CHOICES = [
        (PICKUP, 'Pick-up'),
        (DELIVERY, 'Delivery'),
    ]

    name           = models.CharField(max_length=100)
    email          = models.EmailField()
    phone          = models.CharField(max_length=20)
    choice         = models.CharField(max_length=1, choices=CHOICES)
    date_needed    = models.DateField()
    details        = models.TextField(help_text="Flavors, quantities, special requests")
    paid           = models.BooleanField(default=False)
    checkout_id    = models.CharField(max_length=200, blank=True, null=True)
    created        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.date_needed}"
