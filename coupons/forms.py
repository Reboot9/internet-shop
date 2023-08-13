from django import forms
from coupons.models import Coupon


class CouponForm(forms.Form):
    code = forms.CharField(max_length=100)
