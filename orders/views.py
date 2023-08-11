import weasyprint
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView

from cart.cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem, Order
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

        # start async task to send email
        order_created.delay(order.id)
        # set request in session
        self.request.session['order_id'] = order.id
        # redirect to payment page
        return redirect(reverse('payment:process'))


    def form_invalid(self, form):
        cart = Cart(self.request)
        return render(self.request, self.template_name,
                      {'cart': cart, 'form': form})


@method_decorator(staff_member_required, name='dispatch')
class AdminOrderPDFView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        html = render_to_string('orders/order/pdf_template.html', {'order': order})

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename=order_{order.id}.pdf'

        pdf = weasyprint.HTML(string=html).write_pdf(
            stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
        )
        response.write(pdf)

        return response
