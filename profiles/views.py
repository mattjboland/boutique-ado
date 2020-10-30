# As a final step in this video let's set up the basic URLs views
# and templates for the profiles app.
# Starting with views.py I'll create a simple view called profile.
# And it's just going to return a profile.html template with an
# empty context for now.

from django.shortcuts import render, get_object_or_404
from django.contrib import messages

# Then go to our profiles views. Import the user profile model.
# Get the profile for the current user. And then return it to the template.

from .models import UserProfile

# Let's now go to the profile view import the form.
# Populate it with the user's current profile information.
# And return it to the template.
# We can also get rid of the profile itself in the context now.
# But since will soon render and order history on this page.
# I'll use the profile and the related name on the order model.
# To get the users orders and return those to the template instead.

from .forms import UserProfileForm

from checkout.models import Order


def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    # let's write the post handler for the profile view.
    # It's quite simple all we're going to do is if the request method is post.
    # Create a new instance of the user profile form using the post data.
    # And tell it the instance we're updating is the profile we've just
    # retrieved above. Then if the form is valid. We'll simply save it and add
    # a success message. And that means we'll also need to import messages.

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')

    form = UserProfileForm(instance=profile)
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)


# We won't be able to open the template now since the order history URL
# doesn't exist yet. So let's go create that view and its URL.
# Back in the profile apps views.py I'll create a new view called order_history
# And it will take in the order number as a parameter. The logic for it is
# quite simple. First I'll get the order which means, of course, I'll need to
# import the order model at the top. Then I'll add a message letting the user
# know they're looking at a past order confirmation. And finally, I'll give it
# a template and some context which will include the order number. It will use
# the checkout success template since that template already has the layout for
# rendering a nice order confirmation. And this way we don't have to redo it.
# Instead, I've added another variable to the context called from_profile
# So we can check in that template if the user got there via the order history
# view.

def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)
