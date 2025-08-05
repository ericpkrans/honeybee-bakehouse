from django.db import models

ORDER_CHOICES = [
    ('P', 'Pick-up'),
    ('D', 'Delivery'),
]

class Order(models.Model):
    name             = models.CharField(max_length=100)
    email            = models.EmailField()
    phone            = models.CharField(max_length=20)
    choice           = models.CharField(max_length=1, choices=ORDER_CHOICES)
    date_needed      = models.DateField()
    details          = models.TextField()
    created          = models.DateTimeField(auto_now_add=True)
    checkout_id      = models.CharField(
                         max_length=255,
                         null=True, blank=True,
                         help_text="Square checkout link ID"
                      )
    payment_link_url = models.URLField(
                         max_length=500,
                         null=True, blank=True,
                         help_text="Square-hosted checkout page URL"
                      )

    def __str__(self):
        return f"Order #{self.id} by {self.name}"

