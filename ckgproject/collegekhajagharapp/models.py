from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date
# Create your models here.


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="CKG Staff")
    mobile = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products")
    offer_price = models.PositiveIntegerField()
    normal_price = models.PositiveIntegerField(null=True, blank=True)
    carbohydrate = models.DecimalField(max_digits=5, decimal_places=2)
    protein = models.DecimalField(max_digits=5, decimal_places=2)
    fats = models.DecimalField(max_digits=5, decimal_places=2)
    other_energy = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    view_count = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/images/")

    def __str__(self):
        return self.product.title


class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart Number({1}) of customer {0} ".format(self.customer, str(self.id))


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + " CartProduct: " + str(self.id)


ORDER_STATUS = (
    ("Order Pending", "Order Pending"),
    ("Order Received", "Order Received"),
    ("Order Canceled", "Order Canceled"),
)

METHOD = (
    ("Cash", "Cash"),
    ("Khalti", "Khalti"),
)

class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=30)
    preffered_date_time = models.DateTimeField(auto_now_add=False, auto_now=False)
    mobile = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    order_created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, choices=METHOD, default="Cash On Delivery")
    payment_completed = models.BooleanField(
        default=False, null=True, blank=True)

    def __str__(self):
        return "Order Number({1}) of {0} ".format(self.ordered_by, str(self.id))

    @property
    def time_left_minutes(self):
        timenow = self.preffered_date_time
        now = datetime.now()
        result = timenow - now
        if result >= 0:
            return result.minutes
        else:
            return "Time out"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(max_length=100)

    def __str__(self):
        return self.user.username
