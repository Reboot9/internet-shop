from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView

from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm


class CartAddView(View):
    def dispatch(self, request, *args, **kwargs):
        # allow only POST requests
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)

        return HttpResponseNotAllowed(['POST'])

    def post(self, request, *args, **kwargs):
        cart = Cart(request)

        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product, quantity=cd['quantity'], override_quantity=cd['override'])

        return redirect('cart:cart_detail')


class CartRemoveView(View):
    def dispatch(self, request, *args, **kwargs):
        # allow only POST requests
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)

        return HttpResponseNotAllowed(['POST'])

    def post(self, request, *args, **kwargs):
        cart = Cart(request)

        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)

        return redirect('cart:cart_detail')


class CartDetailView(DetailView):
    template_name = 'cart/detail.html'
    context_object_name = 'cart'

    def get_object(self, queryset=None):
        return Cart(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        for item in self.get_object():
            item['update_quantity_form'] = CartAddProductForm(initial={
                'quantity': item['quantity'],
                'override': True,
            })

        return context
