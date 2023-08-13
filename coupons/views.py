from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import FormView

from coupons.forms import CouponForm
from coupons.models import Coupon


class CouponApplyView(FormView):
    form_class = CouponForm
    def form_valid(self, form):
        now = timezone.now()
        code = form.cleaned_data['code']
        coupon = get_object_or_404(Coupon, code__iexact=code,
                                   valid_from__lte=now,
                                   valid_to__gte=now,
                                   active=True)
        self.request.session['coupon_id'] = coupon.id

        return redirect('cart:cart_detail')