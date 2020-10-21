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

# With those imports done, let's write a few quick model methods.
# In the order model, I'll begin with a method called generate order number.
# And it's prepended with an underscore by convention to indicate it's a
# private method which will only be used inside this class.
# All it's going to do is return uuid.uuid4().hex.upper()
# which will just generate a random string of 32 characters we can use
# as an order number.


def _generate_order_number(self):
    """
    Generate a random, unique order number using UUID
    """
    return uuid.uuid4().hex.upper()

# Also in this model let's write a method to update the total which we
# can do using the aggregate function.
# The way this works is by using the sum function across all the
# line-item total fields for all line items on this order.
# The default behaviour is to add a new field to the query set
# called line-item total sum. Which we can then get and set the order
# total to that. With the order total calculated, we can then
# calculate the delivery cost using the free delivery threshold
# and the standard delivery percentage from our settings file.
# Setting it to zero if the order total is higher than the threshold.
# And then to calculate the grand total
# all we have to do is add the order total and the delivery cost
# together and save the instance.


def update_total(self):
    """
    Update grand total each time a line item is added,
    accounting for delivery costs.
    """
    self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum']
    if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
        self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
    else:
        self.delivery_cost = 0
    self.grand_total = self.order_total + self.delivery_cost
    self.save()

# Next I'll override the default save method.
# So that if the order we're saving right now doesn't
# have an order number.
# We'll call the generate order number method.
# And then execute the original save method.


def save(self, *args, **kwargs):
    """
    Override the original save method to set the order number
    if it hasn't been set already.
    """
    if not self.order_number:
        self.order_number = self._generate_order_number()
    super().save(*args, **kwargs)

# Finally for both of these models.
# I'll add the standard string method,
# returning just the order number for the order model.


def __str__(self):
    return self.order_number


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

# Like setting the order number on the order model we
# also need to set the line-item total field
# on the order line-item model by overriding its save method.
# The logic is simple though, we just need to multiply the
# product price by the quantity for each line item.


def save(self, *args, **kwargs):
    """
    Override the original save method to set the lineitem total
    and update the order total.
    """
    self.lineitem_total = self.product.price * self.quantity
    super().save(*args, **kwargs)


# Finally for both of these models.
# And the SKU of the product along with the order
# number it's part of for each order line item.


def __str__(self):
    return f'SKU {self.product.sku} on order {self.order.order_number}'
