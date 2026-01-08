from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import stripe
from django.conf import settings

from .models import Discount, Item, Order, Tax


@dataclass(frozen=True)
class StripeKeypair:
    secret_key: str
    publishable_key: str


def get_keypair_for_currency(currency: str) -> StripeKeypair:
    c = (currency or "").strip().lower()
    if c == Item.CURRENCY_EUR:
        return StripeKeypair(
            secret_key=settings.STRIPE_EUR_SECRET_KEY,
            publishable_key=settings.STRIPE_EUR_PUBLISHABLE_KEY,
        )
    return StripeKeypair(
        secret_key=settings.STRIPE_USD_SECRET_KEY,
        publishable_key=settings.STRIPE_USD_PUBLISHABLE_KEY,
    )


def money_to_minor(amount: Decimal) -> int:
    q = (amount * Decimal("100")).quantize(Decimal("1"))
    return int(q)


def ensure_coupon(discount: Discount, currency: str) -> str:
    kp = get_keypair_for_currency(currency)
    stripe.api_key = kp.secret_key

    if discount.stripe_coupon_id:
        try:
            stripe.Coupon.retrieve(discount.stripe_coupon_id)
            return discount.stripe_coupon_id
        except Exception:
            pass

    params: Dict[str, Any] = {"name": discount.name}

    if discount.percent_off is not None:
        params["percent_off"] = float(discount.percent_off)
        params["duration"] = "once"
    elif discount.amount_off is not None:
        params["amount_off"] = money_to_minor(discount.amount_off)
        params["currency"] = currency
        params["duration"] = "once"
    else:
        raise ValueError("Discount must have either percent_off or amount_off")

    created = stripe.Coupon.create(**params)
    discount.stripe_coupon_id = created["id"]
    discount.currency = currency
    discount.save(update_fields=["stripe_coupon_id", "currency"])
    return discount.stripe_coupon_id


def ensure_tax_rate(tax: Tax) -> str:
    kp = get_keypair_for_currency(settings.STRIPE_CURRENCY_DEFAULT)
    stripe.api_key = kp.secret_key

    if tax.stripe_tax_rate_id:
        try:
            stripe.TaxRate.retrieve(tax.stripe_tax_rate_id)
            return tax.stripe_tax_rate_id
        except Exception:
            pass

    created = stripe.TaxRate.create(
        display_name=tax.name,
        percentage=float(tax.percentage),
        inclusive=bool(tax.inclusive),
    )
    tax.stripe_tax_rate_id = created["id"]
    tax.save(update_fields=["stripe_tax_rate_id"])
    return tax.stripe_tax_rate_id


def create_checkout_session_for_item(item: Item, request_origin: str) -> Dict[str, Any]:
    kp = get_keypair_for_currency(item.currency)
    stripe.api_key = kp.secret_key

    session = stripe.checkout.Session.create(
        mode="payment",
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": item.currency,
                    "unit_amount": money_to_minor(item.price),
                    "product_data": {
                        "name": item.name,
                        "description": item.description,
                    },
                },
            }
        ],
    )
    return {"id": session["id"], "publishable_key": kp.publishable_key}


def create_checkout_session_for_order(order: Order) -> Dict[str, Any]:
    currency = order.currency()
    kp = get_keypair_for_currency(currency)
    stripe.api_key = kp.secret_key

    order_items = list(order.order_items.select_related("item").all())
    if not order_items:
        raise ValueError("Order has no items")

    line_items: List[Dict[str, Any]] = []
    for oi in order_items:
        line_items.append(
            {
                "quantity": int(oi.quantity),
                "price_data": {
                    "currency": oi.item.currency,
                    "unit_amount": money_to_minor(oi.item.price),
                    "product_data": {
                        "name": oi.item.name,
                        "description": oi.item.description,
                    },
                },
            }
        )

    discounts: List[Dict[str, str]] = []
    if order.discount_id:
        coupon_id = ensure_coupon(order.discount, currency)
        discounts = [{"coupon": coupon_id}]

    tax_rates: Optional[List[str]] = None
    if order.tax_id:
        tax_rate_id = ensure_tax_rate(order.tax)
        tax_rates = [tax_rate_id]

    if tax_rates is not None:
        for li in line_items:
            li["tax_rates"] = tax_rates

    session = stripe.checkout.Session.create(
        mode="payment",
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
        line_items=line_items,
        discounts=discounts if discounts else None,
    )
    return {"id": session["id"], "publishable_key": kp.publishable_key}


def create_payment_intent_for_item(item: Item) -> Dict[str, Any]:
    kp = get_keypair_for_currency(item.currency)
    stripe.api_key = kp.secret_key

    intent = stripe.PaymentIntent.create(
        amount=money_to_minor(item.price),
        currency=item.currency,
        description=item.description or None,
        automatic_payment_methods={"enabled": True},
    )
    return {"client_secret": intent["client_secret"], "publishable_key": kp.publishable_key}
