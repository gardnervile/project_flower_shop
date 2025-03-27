from .models import Category


def get_all_categories():
    """Получить все категории."""
    return Category.objects.all()


def get_category_details(category_id):
    """Получить детали категории по ее ID."""
    try:
        return Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return None


def add_category(name, description):
    """Добавить новую категорию."""
    category = Category(name=name, description=description)
    category.save()
    return category


def update_category(category_id, **kwargs):
    """Обновить данные категории."""
    try:
        category = Category.objects.get(id=category_id)
        for attr, value in kwargs.items():
            setattr(category, attr, value)
        category.save()
        return category
    except Category.DoesNotExist:
        return None


def delete_category(category_id):
    """Удалить категорию по ее ID."""
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        return True
    except Category.DoesNotExist:
        return False
