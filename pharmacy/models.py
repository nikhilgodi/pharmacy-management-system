from django.db import models
from django.contrib.auth.models import User


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    manufacture_date = models.DateField()
    expiry_date = models.DateField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Delivered', 'Delivered'),
        ('Rejected', 'Rejected'),
    ]

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    count = models.PositiveIntegerField(default=1)

    order_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"{self.medicine.name} - {self.count}"
