from .models import Order


def get_all_orders():
    """Получить все заказы."""
    return Order.objects.all()


def get_order_details(order_id):
    """Получить детали заказа по его ID."""
    try:
        return Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return None