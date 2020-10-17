from django import template


register = template.Library()


@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    return price * quantity


"""One thing you may have noticed is the subtotal
column still isn't being
calculated correctly on the shopping bag page.
This is an easy fix which we'll write a custom template filter for.
A useful trick to have in your arsenal.
For this column, the subtotal should be the quantity times the product price.
In a new folder called template tags.
I'll create a file called bag_tools.py
And I'll also create an empty file called __init__ .py
which will ensure that this directory is treated as a Python package
making our bag tools module available for imports and to use in templates.
Now in the bag tools file from django i'll import template.
And then create a function called calc_subtotal
Which takes in a price and a quantity as parameters and simply returns their
irproduct. Now to register this filter we need to create a variable called
register. Which is an instance of template.library
And then use the register filter decorator to register our function as a
template filter. All of this is straight from the django documentation
by the way so if you'd like a deeper explanation of how it works
just go there and look up creating custom template tags and filters.
With the filter finished all we need to do to use it is load it in the
bag template with load bag tools. Then we can pipe the price into it as
the first argument. And send the item quantity as the second.
To make the filter available we'll need to restart the server but doing
so followed by a quick refresh. Shows it's working perfectly. And the
subtotal is now calculated properly."""
