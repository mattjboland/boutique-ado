# I'm just going to copy it from the home app.
# And our view will be check_out.
# And we'll name it check_out as well.


from django.urls import path
from . import views
from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),

    # This url will take the order number as an argument.
    # Call the checkout success view.
    # And be named checkout_success.

    path('checkout_success/<order_number>', views.checkout_success, name='checkout_success'),

    # Then we need to create the url for the new view for cache_checkout_data in 
    # views.py

    path('cache_checkout_data/', views.cache_checkout_data, name='cache_checkout_data'),

    # Before we go much further let's get this thing listening.
    # The first thing we need to do is create a url for it.
    # This can technically live anywhere but since it's related to the
    # checkout app. I'll put it there in its urls.py.
    # I'll call this path WH.
    # And it will return a function called webhook with the name of webhook.
    # The webhook function will live in a file called webhooks.py
    # So just like we import views models and forms.
    # I'll import the webhook function from .webhooks

    path('wh/', webhook, name='webhook'),
]
