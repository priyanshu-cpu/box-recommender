from django.contrib import admin

from .models import Box, Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "length", "width", "height", "weight")


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ("name", "length", "width", "height", "max_weight", "cost")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("__str__", "created_at", "recommended_box")
    readonly_fields = ("recommended_box",)

    def save_related(self, request, form, formsets, change):
        # Items are saved after the order itself, so recompute once they exist.
        super().save_related(request, form, formsets, change)
        form.instance.update_recommendation()
