from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)],
                                           help_text='Percentage value (1 to 99)')

    active = models.BooleanField()

    def __str__(self):
        return self.code
