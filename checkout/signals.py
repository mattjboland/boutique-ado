# I'll import two signals from django.db.models.signals
# post_save and post_delete.
# Post, in this case, means after.
# So this implies these signals are sent by django to the entire application
# after a model instance is saved and after it's deleted respectively.
# To receive these signals we can import receiver from django.dispatch.
# Of course since we'll be listening for signals from the OrderLineItem model
# we'll also need that.
# Let's write a function, I'll call it update_on_save
# And it'll take in parameters of sender, instance, created,
# and keyword arguments.
# This is a special type of function which will handle signals
# from the post_save event.
# So these parameters refer to the sender of the signal.
# In our case OrderLineItem.
# The actual instance of the model that sent it.
# A boolean sent by django referring to whether this is a new instance or
# one being updated.
# And any keyword arguments.
# Our code inside the method is really simple.
# we just have to access instance.order which refers to the order this
# specific line item is related to.
# And call the update_total method on it.
# Now to execute this function anytime the post_save signal is sent.
# I'll use the receiver decorator. Telling it we're receiving post
# saved signals. From the OrderLineItem model.
# To handle updating the various totals when a line item is deleted.
# We can just copy the whole function. Change the signal,
# And remove the created parameter because it's not sent by this signal.
# I'll save that.
# And now to let django know that there's a new signals module with
# some listeners in it.

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItem

@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.order.update_total()

@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    print('delete signal recieved!')
    instance.order.update_total()