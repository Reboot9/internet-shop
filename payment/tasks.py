from celery import shared_task
from io import BytesIO
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order

@shared_task
def payment_completed(order_id):
    """
    Task of sending an e-mail notification when the order is successfully paid
    """
    order = Order.objects.get(id=order_id)
    # create invoice e-mail
    subject = f'Internet Shop - Invoice no. {order_id}'
    message = f'Please, find attached invoice for your recent purchase.'
    email = EmailMessage(subject, message, 'admin@shop.com', [order.email])

    # generate PDF
    html = render_to_string('orders/order/pdf_template.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

    # attach pdf file
    email.attach(f'order_{order_id}.pdf', out.getvalue(), 'application/pdf')

    # send e-mail
    email.send()