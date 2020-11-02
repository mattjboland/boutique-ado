from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm

# Create your views here.


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)


# With the product form ready to go.
# We can now create a view for store owners to add products to the store.
# In the product apps views.py, I'll call this view add_product
# And for now, all it will do is render an empty instance of our form so we can see how it looks.
# It will use a new template which we'll create in a moment called add_product
# And will include a context including the product form.
# This also means we need to import product form, at the top.
# Then create a URL for it.


def add_product(request):
    """ Add a product to the store Let's write the post handler for the add product view.
        In views.py in the products app if the request method is post.
        We'll instantiate a new instance of the product form from request.post and include request .files also
        In order to make sure to capture in the image of the product if one was submitted.
        Then we can simply check if form.is_valid. And if so we'll save it.
        Add a simple success message.
        And redirect to the same view.
        If there are any errors on the form.
        We'll attach a generic error message telling the user to check their form
        which will display the errors.
        Now I'll just move this empty form instantiation here into an else block
        so it doesn't wipe out the form errors.
        On that note, we should take a moment and make that same change on our profile form
        since I just realized it'll have that same issue."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('add_product'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()

        template = 'products/add_product.html'
        context = {
        'form': form,
    }

    return render(request, template, context)
