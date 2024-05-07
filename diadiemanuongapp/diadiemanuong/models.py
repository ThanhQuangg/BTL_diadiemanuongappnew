from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField
from django.db.models import Sum, Avg
from django.db.models.functions import Extract


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
    image = models.ImageField(upload_to="restaurants/%Y/%m", null=True)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_query_name='restaurants')
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        # self.__private_field = "tags"
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

class DonHang(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    so_luong = models.PositiveIntegerField()
    ngay_dat_hang = models.DateTimeField(auto_now_add=True)
    thanh_toan = models.DecimalField(max_digits=10, decimal_places=2)

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



