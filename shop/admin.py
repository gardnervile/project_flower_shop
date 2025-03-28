from django.contrib import admin
from .models import Category, Bouquet, Order, Customer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name", "description")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "bouquet", "quantity", "order_date", "status")
    list_filter = ("status", "order_date")
    search_fields = ("customer__name", "bouquet__name")
    ordering = ("-order_date",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone")

