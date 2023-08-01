from django.shortcuts import render
from django.views.generic import CreateView

from cart.cart import Cart
from .models import OrderItem
from .forms import OrderCreateForm
from .tasks import order_created


class OrderCreateView(CreateView):
    template_name = 'orders/order/create.html'
    form_class = OrderCreateForm

    def form_valid(self, form):
        cart = Cart(self.request)
        order = form.save()

        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'],
                                     price=item['price'], quantity=item['quantity'])
        # clear cart after adding order items to order
        cart.clear()

        # send email notification that order was successfully created
        order_created.delay(order.id)

        return render(self.request,
                      'orders/order/created.html',
                      {'order': order})

    def form_invalid(self, form):
        cart = Cart(self.request)
        return render(self.request, self.template_name,
                      {'cart': cart, 'form': form})
