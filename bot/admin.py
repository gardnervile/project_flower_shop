from django.contrib import admin
from .models import Budget, Bouquet, Occasion, Customer, Order
from django.utils.safestring import mark_safe


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("name", "min_price", "max_price","description")
    verbose_name = "Бюджет"
    verbose_name_plural = "Бюджеты"


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    verbose_name = "Повод"
    verbose_name_plural = "Поводы"


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "budget", "occasion", "is_available", "preview")
    list_filter = ("budget", "occasion", "is_available")
    search_fields = ("name", "description")

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50"/>')
        return "Нет изображения"

    preview.short_description = "Превью"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone")
    verbose_name = "Клиент"
    verbose_name_plural = "Клиенты"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "bouquet", "quantity", "order_date", "status")
    list_filter = ("status", "order_date")
    search_fields = ("customer__name", "bouquet__name")
    verbose_name = "Заказ"
    verbose_name_plural = "Заказы"
