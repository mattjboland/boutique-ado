# I'm just going to copy it from the home app.
# And our view will be check_out.
# And we'll name it check_out as well.


from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),

# As I mentioned earlier it will take the order number as an argument.
# Call the checkout success view.
# And be named checkout_success.

    path('checkout_success/<order_number>', views.checkout_success, name='checkout_success'),
]
