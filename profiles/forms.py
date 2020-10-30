# I'll begin by copying the checkout apps forms.py into the profiles app.
# Obviously, we'll want to change the model we're importing.
# The name of the class and the model in the metaclass.
# Also in the metaclass, rather than having a fields attribute
# well set the exclude attribute and render all fields except
# for the user field since that should never change.
# We can get rid of the full name and email placeholder since those fields
# don't exist on this model.
# And add default in front of all these field names to make them match the
# model. Now I'll change the autofocus to default_phone_number.
# The country field to default_country.
# And everything else can stay the same except I'll change the classes we're
# adding. To make the form match the rest of our theme.

from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }

        self.fields['default_phone_number'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'default_country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'border-black rounded-0 profile-form-input'
            self.fields[field].label = False
