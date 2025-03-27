from .models import Customer, Order


def get_all_customers():
    """Получить всех клиентов."""
    return Customer.objects.all()


def get_customer_details(customer_id):
    """Получить детали клиента по его ID."""
    try:
        return Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return None


def get_customer_orders(customer_id):
    """Получить все заказы клиента по его ID."""
    try:
        customer = Customer.objects.get(id=customer_id)
        return Order.objects.filter(customer=customer)
    except Customer.DoesNotExist:
        return None