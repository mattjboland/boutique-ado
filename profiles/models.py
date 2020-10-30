# The profiles app will serve two purposes. First to provide a user with a
# place to save default delivery information and second to provide them
# with a record of their order history. To do that we'll need a user profile
# model which is attached to the logged-in user.
# And we'll also need to attach the user's profile to all their orders.
# Let's begin by importing the user model.
# And then creating a user profile model which has a one-to-one field attached
# to the user. This is just like a foreign key except that it specifies that
# each user can only have one profile. And each profile can only be attached
# to one user. The rest of the fields in this model are the delivery
# information fields we want the user to be able to provide defaults for.
# These can come directly from the order model. So I'll grab phone number,
# country, postcode, town or city, the street address lines, and county.
# And paste them in here I'll add default to the beginning of each just to
# make it clearer what they are. And the only other difference is that in the
# profile we want all these fields to be optional so I'll provide null equals
# true and blank equals true for each of them. Also since we're using the
# country field we'll need to import that from Django countries.
# I'll now write a quick string method to return the user name.
# And let's also add a quick receiver for the post save event from the user
# model. So that each time a user object is saved. We'll automatically either
# create a profile for them if the user has just been created.
# Or just save the profile to update it if the user already existed.
# In this case by the way, since there's only one signal I'm not putting it in
# a separate signals.py module like we did for the ones on the order model.
# Lastly we need to import post save and receiver in order for the signal to
# work. So I've now got a nice user profile model that will automatically
# create a profile for everyone who signs up.


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    delivery information and order history
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='Country', null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()
