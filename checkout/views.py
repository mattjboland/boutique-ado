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


from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe


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
            order = order_form.save()
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
