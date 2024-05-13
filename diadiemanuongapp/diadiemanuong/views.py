from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views import View
from rest_framework.decorators import action
from rest_framework import viewsets, generics, status, permissions, parsers, filters, request
from rest_framework.response import Response
from . import perms, serializer
from .paginator import RestaurantPaginator, DishPaginator, UserPaginator
from .serializer import CategorySerializer, RestaurantSerializer, DishSerializer, UserSerializer, CommentSerializer, \
    DishSerializerDetail, OrderSerializer, RatingSerializer, OrderDetailSerializer  # OrderDetailSerializer
from .models import Category, Restaurant, Dish, User, Comment, Like, Order, OrderDetail, Rating, PaymentType
from oauth2_provider.models import AccessToken
from django import forms


# Create your views here.

class CategoryViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(methods=['get'], detail=True)
    def restaurants(self, request, pk):
        d = self.get_object().restaurant_set.all()
        return Response(RestaurantSerializer(d, many=True, context={
            'request': request
        }).data, status=status.HTTP_200_OK)


class RestaurantViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    pagination_class = RestaurantPaginator

    # lay query (kw) duoc truyen vao de filter
    def get_queryset(self):
        queries = self.queryset
        q = self.request.query_params.get('q')
        if q:
            queries = queries.filter(name__icontains=q)
        return queries

    # api lien ket restaurant voi dish qua restaurant_id de lay
    # danh sach dish trong restaurant
    @action(methods=['get'], detail=True)
    def dishes(self, request, pk):
        d = self.get_object().dish_set.all()
        return Response(RestaurantSerializer(d, many=True, context={
            'request': request
        }).data, status=status.HTTP_200_OK)


class DishViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    # pagination_class = DishPaginator

    # xác thực quyền
    permission_classes = [permissions.AllowAny()]

    def get_permissions(self):
        if self.action in ['add_comment', 'like', 'rating']:
            return [permissions.IsAuthenticated()]
        return self.permission_classes

    def get_queryset(self):
        queries = self.queryset
        q = self.request.query_params.get('q')
        if q:
            queries = queries.filter(name__icontains=q)
        x = self.request.query_params.get('x')
        if x:
            queries = queries.filter(price__icontains=x)
        return queries

    # api comment
    @action(methods=['post'], url_path="comments", detail=True)
    def add_comment(self, request, pk):
        comment = Comment.objects.create(user=request.user, dish=self.get_object(),
                                         content=request.data.get('content'))
        comment.save()

        return Response(CommentSerializer(comment, context={
            'request': request
        }).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], url_path='ratings', detail=True)
    def create_rating(self, request, pk):
        rating = Rating.objects.create(user=request.user, dish=self.get_object(),
                                       rate=request.data.get('rate'))
        rating.save()
        return Response(RatingSerializer(rating, context={
            'request': request
        }).data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], url_path='comment', detail=True)
    def get_comment(self, request, pk):
        comments = Comment.objects.filter(dish=self.get_object())

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='rating', detail=True)
    def get_rating(self, request, pk):
        ratings = Rating.objects.filter(dish=self.get_object())

        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='like', detail=True)
    def like(self, request, pk):
        like, create = Like.objects.get_or_create(user=request.user, dish=self.get_object())
        if not create:
            like.liked = not like.liked
            like.save()

        return Response(DishSerializerDetail(self.get_object(), context={
            "request": request
        }).data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # xác nhận comment chính chủ (perms.py)
    permission_classes = [perms.OwnerPermission]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]


class RatingViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['post'], url_path='rating', detail=True)
    def create_rating(self, request, pk):
        rating = Rating.objects.create(user=request.user, dish=self.get_object(),
                                       rate=request.data.get('rate'))
        rating.save()
        return Response(RatingSerializer(rating.data, context={
            'request': request
        }).data, status=status.HTTP_201_CREATED)


class CategoryView(View):

    def get(self, request):
        cats = Category.objects.all()
        return render(request, 'anuong/list.html', {
            'categories': cats
        })

    def post(self, request):
        pass


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPaginator
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser]

    # xác nhận quyền
    def get_permissions(self):
        if self.action in ['get_current']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    # api lấy user gần nhất
    @action(methods=['get'], url_path="current", detail=False)
    def get_current(self, request):
        return Response(UserSerializer(request.user, context={
            "request": request
        }).data, status=status.HTTP_200_OK)

    # api get user
    @action(methods=['get'], url_path="current", detail=False)
    def user_info(request):
        access_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        token = AccessToken.objects.get(token=access_token)
        user = token.user
        # Lấy thông tin người dùng và xử lý
        return Response({'message': 'Hello, ' + user.username})

    def admin_approval_required(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role != 'admin':
                return HttpResponseForbidden("You don't have permission to access this page.")
            return view_func(request, *args, **kwargs)

        return _wrapped_view
class OrderViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


    @action(methods=['POST'], detail=False)
    def create_order(self, request):
        # user = request.user
        address = request.data.get('address')
        shipping_fee = request.data.get('shipping_fee')
        note = request.data.get('note')
        total_amount = request.data.get('total_amount')
        # status_pay = request.data.get('status_pay')
        # status_order = request.data.get('status_order')
        user = int(request.data.get('user_id'))
        paymentType_id = int(request.data.get('paymentType_id'))
        # status_pay = 1 if paymentType_id == 2 else 0

        if request.user.is_authenticated:
            if not address or not shipping_fee or not note or not paymentType_id:
                return Response({'error': 'Thông tin  không đủ'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                return Response("Không tìm thấy tài khoản.", status=status.HTTP_400_BAD_REQUEST)

            try:
                payment_type = PaymentType.objects.get(id=paymentType_id)
            except PaymentType.DoesNotExist:
                return Response("Không tìm thấy loại thanh toán.", status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(address=address, shipping_fee=shipping_fee, note=note,
                                         total_amount=total_amount, user=user, paymentType=payment_type)

            order.save()
            return Response(serializer.OrderSerializer(order).data, status=status.HTTP_200_OK)
        else:
            return Response('Bạn Không có quyền mua hàng')

    @action(methods=['POST'], detail=True)
    def create_orderdetail(self, request, pk):
        order_id = Order.objects.get(pk=pk)
        dish_ids = request.data.get('dish_id', [])
        quantities = request.data.get('quantity', [])
        restaurant_id = request.data.get('restaurant_id')
        total = request.data.get('total')
        user = int(request.data.get('user_id'))
        orderdetails = []
        if request.user.is_authenticated:
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                return Response("Không tìm thấy tài khoản.", status=status.HTTP_400_BAD_REQUEST)
        for dish_id, quantity_pro in zip(dish_ids, quantities):
            dish = Dish.objects.get(pk=dish_id)

            if dish.quantity < int(quantity_pro):
                return Response({'error': 'Không đủ số lượng sản phẩm trong kho'}, status=status.HTTP_400_BAD_REQUEST)

            orderdetail, created = OrderDetail.objects.get_or_create(dish=dish, quantity=quantity_pro,
                                                                     order=order_id, total=total, user=user,
                                                                     restaurant_id=restaurant_id)

            dish.quantity -= int(quantity_pro)
            dish.save()

            total_price = dish.price * int(quantity_pro)
            total += total_price
            orderdetails.append(orderdetail)

        return Response({'order_detail': OrderDetailSerializer(orderdetails, many=True).data, 'total': total})



    @action(detail=False, methods=['GET'])

    def get_orders_confirm_by_account(self, request):

        user_id = int(request.data.get('user_id'))
        if not user_id:
            return Response({'error': 'Missing account ID'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

        orders = Order.objects.filter(user=user).order_by('-id')
        order_details_data = []

        for order in orders:
            order_details = OrderDetail.objects.filter(order=order)
            serialized_order_details = OrderDetailSerializer(order_details, many=True).data

            order_data = {
                'id': order.id,
                'address': order.address,
                'note': order.note,
                'shipping_fee': order.shipping_fee,
                'order_date': order.order_date,
                'paymentType': order.paymentType.id,
                'order_details': serialized_order_details,

            }

            order_details_data.append(order_data)

        return Response(order_details_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_order_detail(self, request):
        order_id = int(request.data.get('order_id'))
        if not order_id:
            return Response({'error': 'Missing order ID'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        order_details = OrderDetail.objects.filter(order=order)
        data = []
        for detail in order_details:
            detail_data = {
                'dish_name': detail.dish.name,
                'quantity': detail.quantity,
                'total': detail.total,
                'restaurant_name': detail.restaurant.name,
            }
            data.append(detail_data)
        return Response(data, status=status.HTTP_200_OK)

class OrderDetailViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]




class PaymentViewSet(viewsets.ViewSet, generics.ListAPIView,
                     generics.CreateAPIView, generics.UpdateAPIView,
                     generics.DestroyAPIView):
    queryset = PaymentType.objects.all()
    serializer_class = serializer.PaymentTypeSerializer



# class CustomUserRegistrationForm(forms.ModelForm):
#     password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
#
#     class Meta:
#         model = CustomUser
#         fields = ['username', 'email', 'password1', 'password2']
#
#     def clean_password2(self):
#         password1 = self.cleaned_data.get("password1")
#         password2 = self.cleaned_data.get("password2")
#         if password1 and password2 and password1 != password2:
#             raise forms.ValidationError("Passwords don't match")
#         return password2
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.status = CustomUser.PENDING
#         if commit:
#             user.save()
#         return user