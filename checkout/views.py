# Let's create a checkout view. Give it a URL and start a
# basic template for it. Starting in views.py let's create
# a checkout view. For now it'll be pretty simple.
# First I'll get the bag from the session.
# And if there's nothing in the bag just add a simple error
# message. And redirect back to the products page.
# This will prevent people from manually accessing the URL
# by typing /checkout. Next we just need to create an
# instance of our order form. Which will be empty for now.
# Then create the template.
# And the context containing the order form.
# And finally render it all out.
# We do need a couple imports at the top.
# We'll need to add redirect and reverse.
# Then messages from django.contrib
# And, of course, the order form.

# In checkouts.view.py.
# At the top I'm going to import the bag contents function from bag.context.
# Which as you know makes that function available for use here in our views.
# Since really all that function returns is a Python dictionary.
# We can pass it the request and get the same dictionary here in the view.
# I'll store that in a variable called current bag.
# Making sure not to overwrite the bag variable that already exists
# And now to get the total all I need to do is get the grand_total key
# out of the current bag.
# I'll multiply that by a hundred and round it to zero decimal places
# using the round function.
# Since stripe will require the amount to charge as an integer.


from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem

from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from bag.contexts import bag_contents

import stripe
import json

# There's one small problem though and that's that we don't have a way to
# determine in the webhook whether the user had the save info box checked.
# Luckily there's a place we can add that to the payment intent
# in a key called metadata, but we have to do it from the
# server-side because the confirm card payment method doesn't support adding
# it. It's not that hard though we can actually just write a simple view to
# take care of it. let's head over to views.py and make a quick view called
# cash_checkout_data. We'll expect only the post method here so I'll use
# the require_POST decorator and let's import that, an HttpResponse up here
# at the top. What's gonna happen here is before we call the confirm card
# payment method in the stripe JavaScript. we'll make a post request to
# this view and give it the client secret from the payment intent. If we
# split that at the word secret the first part of it will be the payment
# intent Id, so I'll store that in a variable called pid. Then I'll set
# up stripe with the secret key so we can modify the payment intent.
# To do it all we have to do is call stripe.PaymentIntent.modify
# give it the pid, and tell it what we want to modify in our case we'll add
# some metadata. Let's add the user who's placing the order.
# Will add whether or not they wanted to save their information.
# And most importantly we'll add a JSON dump of their shopping bag which we'll
# use a little later. I'll also import JSON up here since we're using that to
# add the bag to the metadata. After adding that stuff all we need to do is
# return an HTTP response with the status of 200 for okay.
# And let's wrap the whole thing in a try-except block.
# And if anything goes wrong we'll just add a message and return a response
# with the error message content and a status of 400 for bad request.
# This way we can post to the view from JavaScript
# and if everything goes ok we should get a 200 response.


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


# With those variables set and our settings saved.
# I can now go back to the checkout views and create the
# payment intent. First I'll set a couple of variables for
# the public and secret keys all the way at the top.
# Then I need to set the secret key on stripe.
# And then we can create the payment intent with
# stripe.payment.intent.create
# giving it the amount and the currency.
# For now, let's just print it out.
def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

# To confirm it we verified that the form on the checkout page was submitted.
# However, at the moment the form data doesn't actually go anywhere
# since the checkout view doesn't have any handling for the post method.
# Let's fix that in this video. So that when a user submits their payment
# information. We also create the order in the database.
# And redirect them to a success page.
# The first thing to do is obviously check whether the method is post.
# That means we should also wrap the current code into an else block to
# handle the get requests.
# In the post method code we will need the shopping bag.
# And then we'll put the form data into a dictionary.
# I'm doing this manually in order to skip the save infobox
# which doesn't have a field on the order model.
# All the other fields can come directly from the form though.
# And then we can create an instance of the form using the form data.
# If the form is valid we'll save the order.
# And then we need to iterate through the bag items to create each line item.
# This code is pretty similar to what we used in the context processor.
# So I'll just paste it in and review it briefly.
# First we get the Product ID out of the bag.
# Then if its value is an integer we
# know we're working with an item that doesn't have sizes.
# So the quantity will just be the item data.
# Otherwise, if the item has sizes. we'll iterate through each size and
# create a line item accordingly.
# Finally this should theoretically never happen but just in case a
# product isn't found we'll add an error message.
# Delete the empty order and return the user to the shopping bag page.
# At the bottom here at the same indentation level as the for-loop.
# We'll attach whether or not the user wanted to save their profile
# information to the session.
# And then redirect them to a new page which we'll create in just a moment.
# We'll name the new URL check out success.
# And pass it the order number as an argument.
# Also to get that we'll need to save the order here on line 31 so
# I'll add that. If the order form isn't valid let's just attach a message
# letting them know and they'll be sent back to the checkout page at the
# bottom of this view with the form errors shown.

    if request.method == 'POST':
        bag = request.session.get('bag', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
            for item_id, item_data in bag.items():
                try:
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
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')

    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        # Attempt to prefill the form with any info the user maintains in their profile
        # All we need to do is check whether the user is authenticated.
        # And if so we'll get their profile and use the initial parameter on the order form
        # to pre-fill all its fields with the relevant information.
        # For example, we can fill in the full_name with the built in get_full_name method on their user account.
        # Their email from their user account.
        # And everything else from the default information in their profile.
        # If the user is not authenticated we'll just render an empty form.

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


# Before creating the checkout success view. Let's make sure to import our two models at the top.
# We need the product model from the products app.
# And OrderLineItem from this app.
# With that done we can move on to creating the checkout success view.

# This is simply going to take the order number and render a nice success page
# letting the user know that their payment is complete.
# In this view we'll want to first check whether the
# user wanted to save their information by getting that from the session just like
# we get the shopping bag.
# For now, we won't do anything with this but it'll be required once we create user profiles.
# In the meantime let's use the order number to get the order created in the previous view
# which we'll send back to the template.
# Then I'll attach a success message letting the user know what their order number is.
# And that will be sending an email to the email they put in the form.
# Finally, I'll delete the user shopping bag from the session
# since it'll no longer be needed for this session.
# Set the template and the context.
# And render the template.
# We'll need to import our order model at the top now as well as get_object_or_404.
# And then head to urls.py to create the URL.


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

    # Save the user's info
    if save_info:
        profile_data = {
            'default_phone_number': order.phone_number,
            'default_country': order.country,
            'default_postcode': order.postcode,
            'default_town_or_city': order.town_or_city,
            'default_street_address1': order.street_address1,
            'default_street_address2': order.street_address2,
            'default_county': order.county,
        }
        user_profile_form = UserProfileForm(profile_data, instance=profile)
        if user_profile_form.is_valid():
            user_profile_form.save()

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
