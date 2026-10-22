from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

POSITIVE = [MinValueValidator(Decimal("0.01"))]


def dimension_field():
    return models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)


class Product(models.Model):
    """A sellable item. Dimensions in cm, weight in kg."""

    name = models.CharField(max_length=200)
    length = dimension_field()
    width = dimension_field()
    height = dimension_field()
    weight = dimension_field()

    def __str__(self):
        return self.name

    @property
    def dimensions(self):
        return (self.length, self.width, self.height)


class Box(models.Model):
    """A shipping box. Internal dimensions in cm, capacity in kg."""

    name = models.CharField(max_length=100)
    length = dimension_field()
    width = dimension_field()
    height = dimension_field()
    max_weight = dimension_field()
    cost = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name_plural = "boxes"

    def __str__(self):
        return f"{self.name} ({self.length}x{self.width}x{self.height} cm)"

    @property
    def dimensions(self):
        return (self.length, self.width, self.height)

    @property
    def volume(self):
        return self.length * self.width * self.height


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    recommended_box = models.ForeignKey(
        Box, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )

    def __str__(self):
        return f"Order #{self.pk}"

    def update_recommendation(self):
        from .services import recommend_box

        self.recommended_box = recommend_box(
            (item.product, item.quantity) for item in self.items.select_related("product")
        )
        self.save(update_fields=["recommended_box"])
        return self.recommended_box


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.quantity} x {self.product}"
