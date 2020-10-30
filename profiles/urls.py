# Let's go create the URL for this view.
# And then include the URLs in the project level file.
# urls.py in boutique_ado

from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile')
]