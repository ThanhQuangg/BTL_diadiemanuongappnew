from .models import Category, Restaurant, Dish, Tag, User, Comment, Order, OrderDetail, Rating, \
    PaymentType
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
        fields = ['id', 'name', 'description', 'created_date', 'updated_date', 'image',  'price', 'tags']


class DishSerializerDetail(DishSerializer):
    liked = serializers.SerializerMethodField()

    def get_liked(self, dish):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return dish.like_set.filter(liked=True, user=request.user).exists()

    class Meta:
        model = DishSerializer.Meta.model
        fields = DishSerializer.Meta.fields + ['liked']


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


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'created_date', 'updated_date']


class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Rating
        fields = ['id', 'rate', 'user']


class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    paymentType = PaymentTypeSerializer(read_only=True)


    class Meta:
        model = Order
        fields = ["id", "address", "note", "shipping_fee",
                  "order_date", "user_info", "paymentType"]


class OrderDetailSerializer(serializers.ModelSerializer):
    dish = DishSerializer()

    class Meta:
        model = OrderDetail
        fields = ["id", "dish", "quantity", "order", "user", "total", "restaurant"]


