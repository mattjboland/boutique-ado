# We've completed all but the last few user stories now. So for the next few
# videos we'll spend our time giving store owners defined as those who are superusers
# in Django the ability to add, update, and delete products in the store.
# We've got most of the infrastructure for this already built.
# But we will need a product form.
# Let's create a forms.py in the products app.
# Firstly we need some imports including forms from Django.
# And our product and category models from this app.
# Now we can create a new class, ProductForm which will extend the built
# in forms.model form.
# And have an inner metaclass that defines the model and the fields we want to include.
# In this case I'm using a special dunder or double underscore string
# called all which will include all the fields.
# Then I'm going to override the init method to make a couple changes to the fields.
# We'll want the categories to show up in the form using their friendly name.
# So let's get all the categories.
# And create a list of tuples of the friendly names associated with their category ids.
# This special syntax is called the list comprehension.
# And is just a shorthand way of creating a for loop that adds items to a list.
# Now that we have the friendly names, let's update the category field on the form.
# To use those for choices instead of using the id.
# The effect of this will be seen in the select box that gets generated in the form.
# Instead of seeing the category ID or the name field we'll see the friendly name.
# Finally I'll just iterate through the rest of these fields
# and set some classes on them to make them match the theme of the rest of our store.

from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(label='Image', required=False, widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
