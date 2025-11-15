from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
from django.utils import timezone
# Create your models here.

class MyUser(models.Model):
    user_id = models.AutoField(primary_key=True)  
    user_name = models.CharField(max_length=100)
    user_email = models.CharField(max_length=255)
    user_number = models.CharField(max_length=15)
    user_password = models.CharField(max_length=255)
    role = models.CharField(max_length=200, default='client')
    class Meta:
	    db_table="user_details"
          

# class Product(models.Model):
#     product_name = models.CharField(max_length=255)
#     product_price = models.DecimalField(max_digits=10, decimal_places=2)
#     product_stock = models.IntegerField()
#     product_category = models.CharField(max_length=100, blank=True, null=True)
#     product_description = models.TextField(blank=True, null=True)
#     product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)

#     def __str__(self):
#         return self.product_name

from django.db import models

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_stock = models.IntegerField()
    product_category = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_image = models.ImageField(upload_to='products/')

    class Meta:
        db_table = "mystore_product" 

class Cart(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_cart"
        unique_together = ("user", "product")  # prevent duplicate entries

    def __str__(self):
        return f"{self.user.user_name} - {self.product.product_name} ({self.quantity})"

    @property
    def total_price(self):
        return self.quantity * self.product.product_price
    

class Order(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    warranty_number = models.CharField(max_length=50, unique=True, blank=True)
    warranty_end = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, default="Not Paid")
    address =  models.TextField(max_length=200, null=True)
    status = models.CharField(max_length=100, default="processing")
    def save(self, *args, **kwargs):
        if not self.warranty_number:
            self.warranty_number = str(uuid.uuid4()).replace("-", "").upper()[:12]
        if not self.warranty_end:
            self.warranty_end = timezone.now() + timedelta(days=180)  # 6 months warranty
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.product.product_name} ({self.quantity})"


class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    issue = models.TextField(max_length=500)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open')
    assigned_staff = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "support_tickets"

    def __str__(self):
        return f"Ticket #{self.id} - {self.product.product_name} ({self.status})"
