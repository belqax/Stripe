from __future__ import annotations

from decimal import Decimal
from django.db import models


class Item(models.Model):
    CURRENCY_USD = "usd"
    CURRENCY_EUR = "eur"

    CURRENCY_CHOICES = [
        (CURRENCY_USD, "USD"),
        (CURRENCY_EUR, "EUR"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_USD)

    def __str__(self) -> str:
        return f"{self.name} ({self.currency.upper()} {self.price})"


class Discount(models.Model):
    name = models.CharField(max_length=255)
    percent_off = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    amount_off = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default=Item.CURRENCY_USD)
    stripe_coupon_id = models.CharField(max_length=255, blank=True, default="")

    def __str__(self) -> str:
        return self.name


class Tax(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(max_digits=6, decimal_places=3)
    inclusive = models.BooleanField(default=False)
    stripe_tax_rate_id = models.CharField(max_length=255, blank=True, default="")

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    name = models.CharField(max_length=255, blank=True, default="")
    items = models.ManyToManyField(Item, through="OrderItem", related_name="orders")
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
    tax = models.ForeignKey(Tax, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Order #{self.id}"

    def currency(self) -> str:
        first = self.order_items.select_related("item").first()
        if not first:
            return Item.CURRENCY_USD
        return first.item.currency

    def subtotal(self) -> Decimal:
        total = Decimal("0.00")
        for oi in self.order_items.select_related("item").all():
            total += oi.item.price * oi.quantity
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name="order_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [("order", "item")]

    def __str__(self) -> str:
        return f"Order #{self.order_id} - {self.item_id} x {self.quantity}"
