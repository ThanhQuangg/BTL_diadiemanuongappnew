from rest_framework.serializers import ModelSerializer

from .models import Category, Restaurant, Dish, Tag, User, Comment, Order, OrderDetail, Rating, \
    PaymentType, UserRole
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='image')

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri("/static/%s" % obj.image.name)
            return "/static/%s" % obj.image.name

    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar']
        # không hiển thị lại password
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

        # băm password

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(data['password'])
        user.save()

        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class RestaurantSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    image = serializers.SerializerMethodField(source='image')

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri("/static/%s" % obj.image.name)
            return "/static/%s" % obj.image.name

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'image', 'description', 'price', 'tags']
        # read_only_fields = ['is_approved', 'user']  # Prevent these fields from being set via the API

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        restaurant = Restaurant.objects.create(**validated_data)
        for tag_data in tags_data:
            Tag.objects.create(restaurant=restaurant, **tag_data)
        return restaurant


class DishSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    image = serializers.SerializerMethodField(source='image')

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri("/static/%s" % obj.image.name)
            return "/static/%s" % obj.image.name

    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'created_date', 'updated_date', 'image', 'price', 'tags']


class DishSerializerDetail(DishSerializer):
    liked = serializers.SerializerMethodField()

    def get_liked(self, dish):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return dish.like_set.filter(liked=True, user=request.user).exists()

    class Meta:
        model = DishSerializer.Meta.model
        fields = DishSerializer.Meta.fields + ['liked']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'created_date', 'updated_date']


class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Rating
        fields = ['id', 'rate', 'user', 'created_date', 'updated_date']


class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    paymentType_info = PaymentTypeSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "address", "note", "shipping_fee",
                  "order_date", "user_info", "paymentType_info"]
        # , "restaurant"]


class OrderDetailSerializer(serializers.ModelSerializer):
    dish_info = DishSerializer(source='dish', read_only=True)
    order_info = OrderSerializer(source='order', read_only=True)

    class Meta:
        model = OrderDetail
        fields = ["id", "dish_info", "quantity", "user", "total", "restaurant", 'order_info']


class RoleSerializer(ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', "name_role"]
