# Let's go create the URL for this view.
# And then include the URLs in the project level file.
# urls.py in boutique_ado

from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),

    # With that complete, I'll go create the URL for it.
    # The URL will be order_history followed by the order_number.
    # It'll return that view and have a matching name.

    path('order_history/<order_number>', views.order_history, name='order_history'),
]
