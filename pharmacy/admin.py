from django.contrib import admin
from .models import Medicine, Order


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'manufacture_date',
        'expiry_date',
        'price',
        'count',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'medicine',
        'user',
        'count',
        'order_date',
        'status',
    )