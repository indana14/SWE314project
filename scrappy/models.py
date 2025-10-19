from django.db import models
from django.contrib.auth.models import AbstractUser


# Extend Django User for phone-based login
class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["username", "email"]

    def __str__(self):
        return self.username


# Category (Admin defines base price per kg)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.base_price} per kg)"


# Seller Profile
class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    total_sold = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def update_stats(self):
        sold_products = self.products.filter(approved=True)
        self.total_sold = sum(p.weight for p in sold_products)
        self.total_earnings = sum(p.price for p in sold_products)
        self.save()

    def __str__(self):
        return f"Seller: {self.user.username}"


# Product Model (✅ available_date removed)
class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    approved = models.BooleanField(default=False)  # Admin approval required

    def save(self, *args, **kwargs):
        # Auto-calc price before saving
        if self.category and self.weight:
            self.price = self.category.base_price * self.weight
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# Cart Item Model
class CartItem(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"
