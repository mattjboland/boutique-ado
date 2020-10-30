# As a final step in this video let's set up the basic URLs views
# and templates for the profiles app.
# Starting with views.py I'll create a simple view called profile.
# And it's just going to return a profile.html template with an
# empty context for now.

from django.shortcuts import render, get_object_or_404

# Then go to our profiles views. Import the user profile model.
# Get the profile for the current user. And then return it to the template.

from .models import UserProfile


def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    template = 'profiles/profile.html'
    context = {
        'profile': profile,
    }

    return render(request, template, context)
