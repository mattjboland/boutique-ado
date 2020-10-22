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


from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
    }

    return render(request, template, context)
