import csv
import datetime
from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    fields = ['product', 'price', 'quantity', 'item_total']
    readonly_fields = ['item_total']
    extra = 1

    def item_total(self, instance):
        try:
            return instance.get_cost()
        except TypeError:
            return 0

    item_total.short_description = 'Item Total'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


def order_stripe_payment(obj):
    """
        Generates a Stripe payment URL link for the given Order model object.

        :param obj: Order model object
        :return: A string containing an HTML link to the Stripe payment URL if `stripe_id` exists in the object,
         otherwise an empty string.
    """
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)

    return ''


order_stripe_payment.short_description = 'Stripe payment'


@admin.action(description='Export to CSV')
def export_to_csv(modeladmin, request, queryset):
    """
        Custom admin action to export selected model objects to a CSV file.

        :param modeladmin: The ModelAdmin instance.
        :param request: The current request.
        :param queryset: A queryset containing the selected objects to be exported.
        :return: An HttpResponse with the CSV content attached as a file download.
    """
    opts = modeladmin.model._meta

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={opts.verbose_name}.csv'
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not \
        field.many_to_many and not field.one_to_many]

    # write row with header info
    writer.writerow([field.verbose_name for field in fields])

    # write data to csv file
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')

            data_row.append(value)
        writer.writerow(data_row)
    return response


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code',
                    'city', 'paid', order_stripe_payment, 'created', 'updated',
                    'total_cost']

    fields = ('first_name', 'last_name', 'email', 'address', 'postal_code',
              'city', 'paid', 'total_cost')

    readonly_fields = ('created', 'updated', 'total_cost')

    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]

    def total_cost(self, instance):
        return instance.get_total_cost()
