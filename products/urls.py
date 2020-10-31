from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),

    # I'll add a new URL called add, which will point to the add_product view.
    # And have a name of add_product.
    # We'll also need to update the product detail URL slightly
    # to specify that the product ID should be an integer.
    # Since otherwise navigating to products /add will interpret the string add as a product id.
    # Which will cause that view to throw an error.

    path('add/', views.add_product, name='add_product'),
]
