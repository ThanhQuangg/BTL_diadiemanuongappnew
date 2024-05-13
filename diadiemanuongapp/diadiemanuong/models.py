from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField


# class CustomUser(AbstractUser):
#     PENDING = 'pending'
#     APPROVED = 'approved'
#     REJECTED = 'rejected'
#
#     STATUS_CHOICES = [
#         (PENDING, 'Pending'),
#         (APPROVED, 'Approved'),
#         (REJECTED, 'Rejected'),
#     ]
#
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)


class User(AbstractUser):
    avatar = CloudinaryField('avatar', null=True)
    # full_name = models.CharField(max_length=255, null=True)
    # date_of_birth = models.DateField(null=True)
    # gender = models.BooleanField(null=True)
    address = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=15, null=True)
    # role = models.ForeignKey(UserRole, on_delete=models.CASCADE, related_name="roles", null=True)
    # social_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

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
    quantity = models.IntegerField(null= True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        # self.__private_field = "tags"
        return self.name

    # danh mục không được trùng nhau
    # class Meta:
    #     unique_together = ('name', 'restaurant')


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
    rate = models.DecimalField(max_digits=5, decimal_places=2)


class PaymentType(models.Model):
    name_paymentType = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name_paymentType


class Order(BaseModel):
    address = models.CharField(max_length=255)
    shipping_fee = models.FloatField()
    note = models.TextField(null=True)
    # status_pay = models.BooleanField(default=False)
    # status_order = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    paymentType = models.ForeignKey(PaymentType, on_delete=models.CASCADE, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "Đơn hàng [" + self.user.username + "]" + " + Địa chỉ [" + self.address + "]"


class OrderDetail(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    # price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.dish.name_product + " - Đơn hàng [username: " + self.order.user.username + "]"

