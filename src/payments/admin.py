from __future__ import annotations

from django.contrib import admin

from .models import Discount, Item, Order, OrderItem, Tax


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "currency", "price")
    search_fields = ("name",)
    list_filter = ("currency",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "item", "quantity")
    autocomplete_fields = ("order", "item")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ("item",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    inlines = [OrderItemInline]
    autocomplete_fields = ("discount", "tax")


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "percent_off", "amount_off", "currency", "stripe_coupon_id")
    search_fields = ("name",)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "percentage", "inclusive", "stripe_tax_rate_id")
    search_fields = ("name",)
