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
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    # I'll set it up to actually listen for webhooks.
    # Both of these new methods will be a carbon copy of the existing one but
    # I'll change the names. The idea here is that for each type of webhook.
    # We want a different method to handle it which makes them easy to manage.
    # And makes it easy to add more as stripe adds new ones.
    # The first method is called handle_payment_intent_succeeded
    # And as you might guess its job is to handle the payment intent succeeded
    # webhook from stripe. This will be sent each time a user completes the
    # payment process. In the event of their payment failing we'll have a
    # separate method listening for that webhook.
    # Just to designate that the generic handle event method
    # here is receiving the webhook we are otherwise not handling
    # Let's change the content to unhandled webhook receive.
    # You'll see what this does in a few minutes.
    # Before we go much further let's get this thing listening.

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        # Anyway with all this finished let's head
        # to the webhook Handler and print out the payment intent coming from
        # stripe once the user makes a payment. With any luck it should have
        # our metadata attached. The payment intent will be saved in a key
        # called event.data.object. So we'll store that and print it out.
        intent = event.data.object
        print(intent)
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
