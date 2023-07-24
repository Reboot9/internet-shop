from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from .models import Category, Product
from cart.forms import CartAddProductForm


class ProductListView(ListView):
    model = Product
    template_name = 'shop/product/list.html'
    # paginate_by = 5
    context_object_name = 'products'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = Product.objects.filter(category=category)
        else:
            queryset = Product.objects.filter(available=True)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()
        context['category'] = self.kwargs.get('category_slug')

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product/detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        id_ = self.kwargs.get('product_id')
        slug = self.kwargs.get('category_slug')

        product = get_object_or_404(Product, id=id_, slug=slug, available=True)

        return product
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_product_form'] = CartAddProductForm()

        return context