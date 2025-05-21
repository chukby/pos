# models.py
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Sale(models.Model):
    DRAFT = 'DR'
    COMPLETED = 'CO'
    CANCELLED = 'CA'
    
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    salesperson = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=DRAFT)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    def update_total(self):
        self.total_amount = sum(item.subtotal for item in self.items.all())
        self.save()

    def __str__(self):
        return f"Sale {self.id} by {self.salesperson.username} on {self.date_created.strftime('%Y-%m-%d %H:%M:%S')}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self):
        return self.quantity * self.price
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} @ {self.price}"
