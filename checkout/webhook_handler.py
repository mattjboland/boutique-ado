# So our form is being submitted and orders are
# successfully created in the database.
# But what happens if the users somehow intentionally or accidentally
# closes the browser window after the payment is confirmed but
# before the form is submitted.
# We would end up with a payment in stripe but no order in our database.
# What's more, if we were building a real store that needed to complete
# post order operations like fulfilment sending internal email
# notifications and so on
# none of that stuff would be triggered because the user never fully
# completed their order.
# This could result in a customer being charged and never receiving a
# confirmation email
# or even worse never receiving what they ordered.
# To prevent this situation we're going to build in some redundancy.
# Each time an event occurs on stripe such as a payment intent being created.
# A payment being completed and so on stripe sends out what's called a
# webhook we can listen for.
# Webhooks are like the signals django sends each time a model is saved
# or deleted.
# Except that they're sent securely from stripe to a URL we specify.
# To handle these webhooks we're going to create our first custom class.
# I'll create a new file here called webhook_handler.py
# And start by importing HttpResponse from django.http
# Now let's create a class called stripeWH_handler
# And give it an init method.
# The init method of the class is a setup method that's called every time
# an instance of the class is created.
# For us we're going to use it to assign the request as an attribute of
# the class
# just in case we need to access any attributes of the request coming
# from stripe.
# Now I'll create a class method called handle event which will take
# the event stripe is sending us
# and simply return an HTTP response indicating it was received.
# With our webhook handler started I'm going to commit my changes.
# And in the next video, we'll add a couple more methods to it and
# start using it to handle webhooks from stripe.

from django.http import HttpResponse


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
