from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.contrib.auth.models import User
from django.conf import settings

class CustomUser(AbstractUser):
    pass

class AdminProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile')
    def __str__(self):
        return f"AdminProfile for {self.user.username}"

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    def __str__(self):
        return f"Customer: {self.user.username}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='items/')
    CATEGORY_CHOICES = [
        ('coffee', 'Coffee'),
        ('snack', 'Snack'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField()
    order_date = models.DateField()
    order_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # <-- ADD THIS

    @property
    def get_total(self):
        return self.quantity * self.item.price

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.quantity}×{self.item.name} in Order {self.order.id}"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.customer.username} - {self.item.name} ({self.reservation_date})"
    
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} for Order {self.order.id}"

class Table(models.Model):
    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Table #{self.table_number} (Capacity: {self.capacity})"

class TableReservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='table_reservations')
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    number_of_guests = models.PositiveIntegerField()
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    special_requests = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-reservation_date', '-reservation_time']
    
    def __str__(self):
        return f"{self.customer.username} - Table #{self.table.table_number} ({self.reservation_date} at {self.reservation_time})"
