from __future__ import annotations

from django.http import Http404, JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET
from django.conf import settings

from .models import Item, Order
from .services import (
    create_checkout_session_for_item,
    create_checkout_session_for_order,
    create_payment_intent_for_item,
    get_keypair_for_currency,
)


@require_GET
def item_page(request: HttpRequest, id: int) -> HttpResponse:
    item = get_object_or_404(Item, pk=id)
    kp = get_keypair_for_currency(item.currency)
    return render(
        request,
        "payments/item_detail.html",
        {
            "item": item,
            "stripe_publishable_key": kp.publishable_key,
            "payment_mode": settings.STRIPE_PAYMENT_MODE,
        },
    )


@require_GET
def buy_item(request: HttpRequest, id: int) -> JsonResponse:
    item = get_object_or_404(Item, pk=id)
    origin = request.build_absolute_uri("/").rstrip("/")
    if settings.STRIPE_PAYMENT_MODE == "payment_intent":
        payload = create_payment_intent_for_item(item)
        return JsonResponse(payload)
    payload = create_checkout_session_for_item(item, origin)
    return JsonResponse(payload)


@require_GET
def order_page(request: HttpRequest, id: int) -> HttpResponse:
    order = get_object_or_404(Order, pk=id)
    currency = order.currency()
    kp = get_keypair_for_currency(currency)
    items = order.order_items.select_related("item").all()
    return render(
        request,
        "payments/order_detail.html",
        {
            "order": order,
            "order_items": items,
            "stripe_publishable_key": kp.publishable_key,
        },
    )


@require_GET
def buy_order(request: HttpRequest, id: int) -> JsonResponse:
    order = get_object_or_404(Order, pk=id)
    payload = create_checkout_session_for_order(order)
    return JsonResponse(payload)


@require_GET
def payment_result(request: HttpRequest, status: str) -> HttpResponse:
    if status not in {"success", "cancel"}:
        raise Http404
    return render(request, "payments/payment_result.html", {"status": status})
