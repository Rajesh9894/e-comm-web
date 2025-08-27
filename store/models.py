from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

class Registerpage(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    
# # Store registered users 
# class RegisterUser(models.Model):
#     username = models.CharField(max_length=150, unique=True)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=128) 
    

#     def __str__(self):
#         return self.username


# Store products
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True) 
    is_new = models.BooleanField(default=False)  

    @property
    def has_discount(self):
        """Check if product has discount"""
        return self.discount > 0

    @property
    def gst_amount(self):
        """Fixed GST amount of ₹50"""
        return 50.00

    @property
    def discounted_price(self):
        """Calculate price after discount and GST: base price + GST - discount"""
        return float(self.price) + self.gst_amount -float(self.discount)

    @property
    def final_price(self):
        """Final price including GST and discount"""
        return self.discounted_price

    def __str__(self):
        return self.name


# Store cart items in DB
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # link to logged-in user
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"


# Store wishlist items
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # link to logged-in user
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate wishlist items

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# Store orders
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=150)
    email = models.EmailField()
    mobile = models.CharField(max_length=15, validators=[RegexValidator(r'^[0-9]{10,15}$', 'Mobile number must contain only numbers and be 10-15 digits long.')])
    address = models.TextField(blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} - {self.product.name}"


# Store product feedback/reviews
class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, 
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'product')  # Prevent duplicate feedback from same user

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.product.name}"
