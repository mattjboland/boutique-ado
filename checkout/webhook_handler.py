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

# to make this work we need a few new imports.
# one is the send mail function from django.core. mail
# And we'll need render_to_string from django.template.loader
# And also our settings file from django.conf
# With these imported, it's easy to send an email.

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from products.models import Product

# Finally we just need to import the user profile model here at the top.

from profiles.models import UserProfile

import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    # To finalize our payment system. let's set it up to send users a confirmation email
    # once their order is completed.
    # The best place to do this is the webhook handler
    # since at that point we know the payment has definitely been made.
    # Since the only thing that can trigger it is a web hook from stripe.
    # First let's write up a quick confirmation email.
    # It'll be split into two text files in the checkout apps templates folder.
    # One called confirmation_email_subject.
    # And the other called confirmation_email_body.
    # In the subject file let's just say Boutique Ado confirmation for order number.
    # And then include the order number using standard django template syntax.
    # These text files can use the exact same syntax as a django template.
    # Because we'll pass them the order when we use them in a few minutes.
    # Now let's write the body of the email.
    # This can say whatever you want, but I'll use the order information to personalize it a bit.
    # I'll include the order number, date, total, delivery costs, and grand total
    # As well as telling the user where it will be shipped and how to contact the store
    # if they need anything.
    # With those two files saved let's head over to the webhook handler
    # and write a new private method called _send_confirmation_email.
    # Don't let this confuse you, even though it's taking in self since it's part of the class
    # it's really not going to do anything special as all, we'll do is give it the order.
    # It just starts with an underscore since it'll only be used inside this class.

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email,
            Let's get the customers email from the order and store it in a variable.
            Then we can use the render_to_string method to render both the files we just created two strings.
            With the first parameter being the file we want to render.
            And the second being at context just like we would pass to a template.
            This is how we'll be able to render the various context variables in the confirmation email.
            I'll pass just the order to the subject.
            And for the body, I'll pass the order as well as a contact email we'll add to the settings file in just a moment.
            Now to finally send the email all we've got to do is use the send mail function.
            Giving it the subject the body the email we want to send from.
            And a list of emails were sending to, which in this case will be only the customer's email.
            So we've got our send confirmation email method complete and it's just expecting
            to be passed an order.
            So to use it we can simply call it anywhere we want to send an email.
            Again since we're doing this in the webhook handler.
            The payment has definitely been completed at this point.
            So we'll want to send an email no matter what."""

        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

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
        """
        In the payment intent succeeded webhook handler we've already got the
        payment intent which has all our customers information in it. All we
        need to do is use it to create an order just like we did with the form.
        The only reason we're doing this is in case the form isn't submitted
        for some reason like if the user closes the page on the loading screen.
        To get started let's get the payment intent id, as well as the
        shopping bag and the users save info preference from the metadata we
        added in the last video. I'll also store the billing details, shipping
        details, and grand_total. All of which we'll need in a moment.
        Now to ensure the data is in the same form as what we want in our
        database. I'll replace any empty strings in the shipping details with
        none. Since stripe will store them as blank strings which is not the
        same as the null value we want in the database. Now that the data is
        clean and ready to go let's talk about the basic process. Most of the
        time when a user checks out, everything will go well and the form will
        be submitted so the order should already be in our database when we
        receive this webhook.
        The first thing then is to check if the order exists already.
        If it does we'll just return a response, and say everything is all set.
        And if it doesn't we'll create it here in the webhook.
        Let's start by assuming the order doesn't exist.
        We can do that with a simple variable set to false.
        Then we'll try to get the order using all the information from the
        payment intent. And I'm using the iexact lookup field to make it an
        exact match but case-insensitive. If the order is found we'll set
        order exists to true, and return a 200 HTTP response to stripe, with
        the message that we verified the order already exists.
        If it doesn't exist let's create it just like we would if the form
        were submitted. In fact, we can get almost all the code we need from
        the view that does the same thing. We'll still want to iterate through
        the bag items, the only difference here is that we're going to load the
        bag from the JSON version in the payment intent
        instead of from the session.
        Also, we don't have a form to save in this webhook to create the order
        but we can do it just as easily with order.objects.create
        using all the data from the payment intent.
        After all, it came from the form originally anyway
        I'll wrap this whole thing in a try block.
        And if anything goes wrong I'll just delete the order if it was
        created. And return a 500 server error response to stripe.
        This will cause stripe to automatically try the webhook again later.
        """
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked

        # We should add this functionality to the webhook handler we wrote as well.
        # So that if the checkout view fails we can depend on the webhook handler to do all the same things.
        # Here in the handle payment intent succeeded method inside our web handler
        # remember that we added that handy key in the payment intent called
        # metadata which contains the username of the user that placed the order.
        # It also contains whether or not they wanted to save their info so
        # let's handle that here. Well begin with profile set to none.
        # Just so we know we can still allow anonymous users to checkout.
        # And you'll see why this matters in a moment.
        # In the meantime, we can get the username from intent.metadata.username
        # And then if the username isn't anonymous user. We know they were authenticated.
        # We could also use request.user here, since we added the request object in the init method above.
        # But this shows you an alternative way to check if the user is authenticated.
        # Anyway, it's they're not anonymous let's try to get their profile using their username.
        # If they've got the save info box checked which again comes from the metadata we added.
        # Then we'll want to update their profile by adding the shipping details
        # as their default delivery information.
        # Then we can just save the profile and we're all set.

        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

        order_exists = False
        # Instead of just immediately going to create the order if it's
        # not found in the database. let's introduce a bit of delay.
        # I'll create a simple variable called attempt and set it to 1.
        # Now let's create a while loop that will execute up to 5 times.
        # I'll move all this code into the loop, but now instead of creating
        # the order if it's not found the first time. I'll increment attempt
        # by 1. And then use pythons time module to sleep for one second.
        # This will in effect cause the webhook handler to try to find the
        # order five times over five seconds before giving up and creating the
        # order itself. Now since the attempt is in a while loop though, if
        # the order is found we should break out of the loop. attempt = 1

        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)

            """If we found the order in the database because it was already created by the form.
            Let's send it just before returning that response to stripe"""

            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,

                    # Now since we've already got their profile and if they weren't logged
                    # in it will just be none.
                    # We can simply add it to their order when the webhook creates it.
                    # In this way, the webhook handler can create orders for both
                    # authenticated users by attaching their profile.
                    # And for anonymous users by setting that field to none.

                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)

        # If the order was created by the webhook handler I'll send the email at
        # the bottom here just before returning that response to stripe.
        # In both cases whether the order already existed or whether the webhook
        # handler just created it. We'll pass it along to our new method in order
        # to send the email.

        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
