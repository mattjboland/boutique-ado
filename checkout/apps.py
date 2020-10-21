# We just need to make a small change to apps.py
# Overriding the ready method and importing our signals module.
# With that done, every time a line item is saved or deleted.
# Our custom update total model method will be called.
# Updating the order totals automatically.

from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    name = 'checkout'


def ready(self):
    import checkout.signals
