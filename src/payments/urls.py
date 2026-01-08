from django.urls import path

from .views import item_page, buy_item, order_page, buy_order, payment_result


urlpatterns = [
    path("item/<int:id>/", item_page, name="item_page"),
    path("buy/<int:id>/", buy_item, name="buy_item"),
    path("order/<int:id>/", order_page, name="order_page"),
    path("buy-order/<int:id>/", buy_order, name="buy_order"),
    path("payments/result/<str:status>/", payment_result, name="payment_result"),
]
