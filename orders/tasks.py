from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
def order_created(order_id):
    """Send email notification when order is successfully created"""
    order = Order.objects.get(id=order_id)

    subject = f'Order №{order.id}'
    message = f'Dear {order.first_name},\n\n' \
              f'You have successfully placed an order №{order.id}.'
    mail_sent = send_mail(subject, message, 'admin@shop.com', [order.email])

    return mail_sent