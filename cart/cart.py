from decimal import Decimal

from django.conf import settings
from django.shortcuts import get_object_or_404

from shop.models import Product
from coupons.models import Coupon


class Cart:
    """Class to control shopping cart"""

    def __init__(self, request):
        """Initialize cart"""

        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save empty cart in session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # save applied coupon
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, quantity=1, override_quantity=False):
        """Add items to the cart or update their quantity"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """Set session as 'modified'"""
        self.session.modified = True

    def remove(self, product):
        """Remove item from cart"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Scroll through the shopping cart items in a loop and get items from the database."""
        product_ids = self.cart.keys()
        # get products and add them to cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Count all items in the cart"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity']
                   for item in self.cart.values())

    def clear(self):
        """Remove cart from session"""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    @property
    def coupon(self):
        if self.coupon_id:
            coupon = get_object_or_404(Coupon, id=self.coupon_id)
            return coupon

        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()

        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
