from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField



class User(AbstractUser):
    avatar = CloudinaryField('avatar', null=True)

    def __str__(self):
        return self.username


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['id']


class Category(BaseModel):
    name = models.CharField(max_length=50, null=False)
    image = models.ImageField(upload_to="category/%Y/%m", null=True)

    def __str__(self):
        return self.name


class Restaurant(BaseModel):
    name = models.CharField(max_length=255, null=False)
    # add ckeditor de format noi dung
    description = RichTextField(null=True)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    image = models.ImageField(upload_to="restaurants/%Y/%m", null=True)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_query_name='restaurants')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.name

    # danh mục không được trùng nhau
    class Meta:
        unique_together = ('name', 'category')


class Dish(BaseModel):
    name = models.CharField(max_length=255)
    # add ckeditor de format noi dung
    description = RichTextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="dish/%Y/%m", null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        # self.__private_field = "tags"
        return self.name

    # danh mục không được trùng nhau
    class Meta:
        unique_together = ('name', 'restaurant')





class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Interaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, null=False)

    class Meta:
        abstract = True


class Comment(Interaction):
    content = models.CharField(max_length=255, null=False)


class Like(Interaction):
    liked = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'dish')


class Rating(Interaction):
    rate = models.SmallIntegerField(default=0)

class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True)
    address = models.CharField(max_length=255)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    payment_method = models.CharField(max_length=50)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='ordersgem', null=True)


    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.PositiveIntegerField()  # Assuming product has an ID field
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_details',null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='items', null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='items', null=True)
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order Detail: {self.order} - {self.product_id} (x{self.quantity})"
