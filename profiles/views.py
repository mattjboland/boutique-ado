# As a final step in this video let's set up the basic URLs views
# and templates for the profiles app.
# Starting with views.py I'll create a simple view called profile.
# And it's just going to return a profile.html template with an
# empty context for now.

from django.shortcuts import render


def profile(request):
    """ Display the user's profile. """

    template = 'profiles/profile.html'
    context = {}

    return render(request, template, context)
