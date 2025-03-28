from .models import Category, Bouquet


def get_all_categories():
    """Получить все категории."""
    return Category.objects.all()


def get_bouquets_by_category(category_id):
    """Получить все букеты по категории."""
    try:
        category = Category.objects.get(id=category_id)
        return Bouquet.objects.filter(category=category)
    except Category.DoesNotExist:
        return None


def add_bouquet(name, price, description, image_url, category_id, is_available=True):
    """Добавить новый букет."""
    try:
        category = Category.objects.get(id=category_id)
        bouquet = Bouquet(
            name=name,
            price=price,
            description=description,
            image_url=image_url,
            category=category,
            is_available=is_available
        )
        bouquet.save()
        return bouquet
    except Category.DoesNotExist:
        return None


def get_bouquet_details(bouquet_id):
    """Получить детали букета по его ID."""
    try:
        return Bouquet.objects.get(id=bouquet_id)
    except Bouquet.DoesNotExist:
        return None


def update_bouquet(bouquet_id, **kwargs):
    """Обновить данные букета."""
    try:
        bouquet = Bouquet.objects.get(id=bouquet_id)
        for attr, value in kwargs.items():
            setattr(bouquet, attr, value)
        bouquet.save()
        return bouquet
    except Bouquet.DoesNotExist:
        return None


def delete_bouquet(bouquet_id):
    """Удалить букет по его ID."""
    try:
        bouquet = Bouquet.objects.get(id=bouquet_id)
        bouquet.delete()
        return True
    except Bouquet.DoesNotExist:
        return False


def is_bouquet_available(bouquet_id):
    """Проверить, есть ли букет в наличии по его ID."""
    bouquet = get_bouquet_details(bouquet_id)
    if bouquet:
        return bouquet.is_available
    return False
