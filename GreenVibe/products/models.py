from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import datetime
import uuid

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class UnitProduct(models.Model):
    unit = models.CharField(max_length=50)

    def __str__(self):
        return self.unit
    
class PKWiU(models.Model):
    number = models.CharField(max_length=20)

    def __str__(self):
        return self.number

class WareHouse(models.Model):
    street = models.CharField(max_length=50)
    number = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)

    def __str__(self):
        return self.city

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    photo = models.ImageField(upload_to='images/products/')
    flavour = models.CharField(max_length=50, default=0)
    description = models.CharField(max_length=2000, default=0)
    composition = models.CharField(max_length=2000, default=0)
    usage = models.CharField(max_length=500, default=0)
    sold = models.PositiveBigIntegerField(default=0)
    product_unit = models.ForeignKey(UnitProduct, on_delete=models.PROTECT, default = 1)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    PKWiU = models.ForeignKey(PKWiU, on_delete=models.PROTECT, default = 1)
    is_active = models.BooleanField(default=True)
    price = models.DecimalField(
        decimal_places = 2,
        max_digits = 20,
        validators = [MinValueValidator(0)]
    )

    def __str__(self):
        return self.name

class ProductStorage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_unit = models.ForeignKey(UnitProduct, on_delete=models.PROTECT, default = 1)
    option = models.CharField(max_length=50, default="300g")
    storage = models.FloatField(default=1000)
    storageJanuary = models.FloatField(default=1000)
    price = models.DecimalField(
        decimal_places = 2,
        max_digits = 20,
        validators = [MinValueValidator(0)],
        default = 0
    )
    priceAll = models.DecimalField(
        decimal_places = 2,
        max_digits = 20,
        validators = [MinValueValidator(0)],
        default = 0
    )
    warehouse = models.ForeignKey(WareHouse, on_delete=models.PROTECT, default = 1)

    @property
    def total_priceAll(self):
        return float(self.storage) * float(self.price)

    def save(self, *args, **kwargs):
        self.priceAll = self.total_priceAll
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.product.name

class UserItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    option = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        decimal_places = 2,
        max_digits = 20,
        validators = [MinValueValidator(0)],
        default = 0
    )

    @property
    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return self.product.name

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    telephone = models.CharField(max_length=10)
    street = models.CharField(max_length=50)
    number = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class Code(models.Model):
    key = models.CharField(max_length=70, default=1)
    code = models.CharField(max_length=20)
    value = models.PositiveIntegerField(default=1)
    is_used = models.BooleanField(default=False)

    def generate_unique_code(self):
        unique_code = str(uuid.uuid4())[:8].upper()
        self.code = f'KOD_{unique_code}'

    def mark_as_used(self):
        self.is_used = True
        self.save()

    def __str__(self):
        return self.code

class DeliveryMethod(models.Model):
    method = models.CharField(max_length=50)
    price = models.DecimalField(
        decimal_places = 2,
        max_digits = 10,
        validators = [MinValueValidator(0)],
    )

    def __str__(self):
        return self.method
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    key_session = models.CharField(max_length=70, default=1)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    telephone = models.CharField(max_length=10)
    street = models.CharField(max_length=50)
    number = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.SET_NULL, null=True, default=1)
    date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.name
    
class OrderHistory(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('Realizacja', 'Realizacja'),
        ('Przesłano', 'Przesłano'),
        ('Doręczono', 'Doręczono'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    option = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        decimal_places = 2,
        max_digits = 20,
        validators = [MinValueValidator(0)],
        default = 0
    )
    priceOrder = models.FloatField(default=0)
    review = models.BooleanField(default=False)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='Realizacja')

    @property
    def total_price(self):
        return self.quantity * self.price
    
    def __str__(self):
        return self.user.username
    
class OrderUserSession(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('Realizacja', 'Realizacja'),
        ('Przesłano', 'Przesłano'),
        ('Doręczono', 'Doręczono'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.CharField(max_length=100)
    key_session = models.CharField(max_length=70)
    option = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        decimal_places = 2,
        max_digits = 20,
        validators = [MinValueValidator(0)],
        default = 0
    )
    priceOrder = models.FloatField(default=0)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='Realizacja')

    @property
    def total_price(self):
        return self.quantity * self.price
    
    def __str__(self):
        return self.key_session
    
class productReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.CharField(max_length=200)
    comment = models.TextField(max_length=300)
    rate = models.FloatField(default=0)
    date = models.DateTimeField(default=datetime.now, blank=True)
    
    def __str__(self):
        return self.product.name

class MonthlyOrderSummary(models.Model):
    month = models.CharField(max_length=50)
    total_value = models.DecimalField(
        max_digits=10,  
        decimal_places=2,  
        validators=[MinValueValidator(0)],
        default=0,
    )

    def __str__(self):
        return f"{self.month} - Total Value: {self.total_value}"
    
class NewDelivery(models.Model):
    date = models.DateTimeField(default=datetime.now, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    option = models.CharField(max_length=50)
    quantity = models.FloatField()

    def __str__(self):
        return self.product.name
    
    def __str__(self):
        return str(self.product) if self.product else "Produkt został usunięty"