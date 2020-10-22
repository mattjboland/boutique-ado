# I'm just going to copy it from the home app.
# And our view will be check_out.
# And we'll name it check_out as well.


from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout')
]
