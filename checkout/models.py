import uuid


# We'll need some imports here at the top.
# Starting with UUID which will be used to generate the order number.
# We'll also need the sum function from django.db.models.
# And our settings module from django.conf
# And of course the product. since the order line item model
# has a foreign key to it.

from django.db import models
from django.db.models import Sum
from django.conf import settings

from products.models import Product


# Create your models here.

# We're gonna dive right into the models here.
# Since we'll need them to create and track orders
# for anyone who makes a purchase.
# I'll create a class called order, here and then paste
# in some fields which we'll review.
# The majority of these are straightforward character
# fields. Most of which are required
# Postcode and County will not be required as those
# components don't exist in every Country.
# We're also using the auto now add attribute on the
# date field which will automatically set the order
# date and time whenever a new order is created.
# And the last three fields will be calculated
# using a model method. Whenever an order is saved.
# One last key thing in this model is the editable
# equals false attribute on the order number field.


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

# Whenever an order is saved.
# One last key thing in this model is the editable equals
# false attribute on the order number field.
# We're gonna automatically generate this order number.
# And we'll want it to be unique and permanent so users
# can find their previous orders.
# So the order model will handle all orders across the store.
# But it's going to be related to another model order line item.
# A line-item will be like an individual shopping bag item.
# Relating to a specific order
# And referencing the product itself. The size that was
# selected. The quantity.
# And the total cost for that line item.
# The basic idea here. Is when a user checks out.
# We'll first use the information they put into the
# payment form to create an order instance.
# And then we'll iterate through the items in the shopping bag.
# Creating an order line item for each one. Attaching it to the order.
# And updating the delivery cost, order total, and grand total along the way.
# On the order line item model. There's a foreign key to the order. With a
# related name of line items. So when accessing orders we'll
#  be able to make calls such as order .lineitems.all
# And order.lineitems.filter
# There's also a foreign key to the product for this line item.
# So that we can access all the fields of the associated product as well.
# The product size is a simple two-character char field.
# Which will be extra-small, small, medium, large, or extra-large.
# And we're allowing that to be null and blank. Since there are some products
# with no sizes.
# Finally we have the quantity and line item total fields, which are both
# required. Though the line item total is not editable.
# Since it'll be automatically calculated when the line item is saved.


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(max_length=2, null=True, blank=True) # XS, S, M, L, XL
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)
