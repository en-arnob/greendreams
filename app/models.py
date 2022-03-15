from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=200)
    joined_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fullname


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


CATEGORIES = (
    ("flower", "flower"),
    ("fruit", "fruit"),
    ("seed", "seed"),
)


class Plant(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    image = models.ImageField(upload_to="plants")
    price = models.PositiveIntegerField()
    description = models.TextField()
    featured = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart: " + str(self.id)


class CartPlant(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + str(self.id)


ORDER_STATUS = (
    ("Order Recieved", "Order Recieved"),
    ("Processing", "Processing"),
    ("On the way", "On the way"),
    ("Completed", "Completed"),
    ("Cancelled", "Cancelled"),
)


class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=250)
    phone = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Order: " + str(self.id)
