from django import forms
from coupons.models import Coupon
from django.utils.translation import gettext_lazy as _


class CouponForm(forms.Form):
    code = forms.CharField(label=_('coupon'), max_length=100)
