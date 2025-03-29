from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Occasion(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Повод"
        verbose_name_plural = "Поводы"

    def __str__(self):
        return self.name


class Bouquet(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to="bouquets/", verbose_name="Изображение", blank=True, null=True)  # Изменено
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    occasion = models.ForeignKey("Occasion", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Повод")
    is_available = models.BooleanField(default=True, verbose_name="В наличии")

    class Meta:
        verbose_name = "Букет"
        verbose_name_plural = "Букеты"

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=15, verbose_name="Телефон")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('ожидание', 'Ожидание'),
        ('завершённый', 'Завершённый'),
        ('отменено', 'Отменено'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Клиент")
    bouquet = models.ForeignKey(Bouquet, on_delete=models.CASCADE, verbose_name="Букет")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ {self.id} от {self.customer.name}"
