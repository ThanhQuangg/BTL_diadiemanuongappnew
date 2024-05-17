from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from rest_framework.decorators import action
from rest_framework import viewsets, generics, status, permissions, parsers, filters, request
from rest_framework.response import Response
from . import perms, serializer
from .paginator import RestaurantPaginator, DishPaginator, UserPaginator
from .serializer import CategorySerializer, RestaurantSerializer, DishSerializer, UserSerializer, CommentSerializer, \
    DishSerializerDetail, OrderSerializer, RatingSerializer, OrderDetailSerializer, RoleSerializer, \
    PaymentTypeSerializer
from rest_framework.utils import json
from django.http import HttpResponse, HttpRequest, JsonResponse
# from django.contrib.admin import action
from django.contrib.auth import authenticate, login

from .models import Category, Restaurant, Dish, User, Comment, Like, Order, OrderDetail, Rating, PaymentType, \
    ActivationRequest, UserRole
from oauth2_provider.models import AccessToken
from django import forms
from rest_framework.parsers import MultiPartParser, JSONParser


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


class RestaurantViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView, generics.CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    # pagination_class = RestaurantPaginator
    permission_classes = [permissions.AllowAny()]

    def get_permissions(self):
        if self.action in ['perform_create', 'get_queryset1', 'perform_update']:
            return [permissions.IsAuthenticated()]
        return self.permission_classes

    # lay query (kw) duoc truyen vao de filter
    def get_queryset(self):
        queries = self.queryset
        q = self.request.query_params.get('q')
        if q:
            queries = queries.filter(name__icontains=q)
        return queries

    # api lien ket restaurant voi dish qua restaurant_id de lay danh sach dish trong restaurant
    @action(methods=['get'], detail=True)
    def dishes(self, request, pk):
        d = self.get_object().dish_set.all()
        return Response(DishSerializerDetail(d, many=True, context={  #RESER
            'request': request
        }).data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_approved=False)  # Lưu người dùng và đặt is_approved thành False

    def get_queryset1(self):
        if self.request.user.is_staff:
            return Restaurant.objects.all()  # Admin có thể xem tất cả các nhà hàng
        return Restaurant.objects.filter(user=self.request.user)  # Người dùng chỉ có thể xem nhà hàng của họ

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(active=False)  # Users can't directly activate restaurants
        else:
            serializer.save()


class DishViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    # pagination_class = DishPaginator

    # xác thực quyền
    permission_classes = [permissions.AllowAny()]

    def get_permissions(self):
        if self.action in ['add_comment', 'like', 'create_rating']:
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

    @action(methods=['get'], detail=False, url_path='search')
    def search(self, request):
        dish_name_query = request.query_params.get('dish_name')
        restaurant_name_query = request.query_params.get('restaurant_name')

        if dish_name_query:
            dishes = Dish.objects.filter(name__icontains=dish_name_query).select_related('restaurant')
            restaurant_ids = dishes.values_list('restaurant_id', flat=True).distinct()
            restaurants = Restaurant.objects.filter(id__in=restaurant_ids)
            serializer = RestaurantSerializer(restaurants, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        if restaurant_name_query:
            restaurants = Restaurant.objects.filter(name__icontains=restaurant_name_query)
            serializer = RestaurantSerializer(restaurants, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'error': 'No query parameters provided.'}, status=status.HTTP_400_BAD_REQUEST)
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
        user = int(request.data.get('user_id'))
        paymentType_id = int(request.data.get('paymentType_id'))
        # restaurant_id = int(request.data.get('restaurant_id'))

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
            # restaurant_id=restaurant_id)

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
        user_id = request.query_params.get('user_id')
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

            id = order.paymentType.id
            paymentType = PaymentType.objects.filter(id=id)
            serialized_paymentType = PaymentTypeSerializer(paymentType, many=True).data

            order_data = {
                'id': order.id,
                'address': order.address,
                'note': order.note,
                'shipping_fee': order.shipping_fee,
                'order_date': order.order_date,
                # 'paymentType': order.paymentType.id,
                'paymentType': serialized_paymentType,
                'order_details': serialized_order_details,
            }
            order_details_data.append(order_data)
        return Response(order_details_data, status=status.HTTP_200_OK)


class OrderDetailViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentViewSet(viewsets.ViewSet, generics.ListAPIView,
                     generics.CreateAPIView, generics.UpdateAPIView,
                     generics.DestroyAPIView):
    queryset = PaymentType.objects.all()
    serializer_class = serializer.PaymentTypeSerializer


class ActivationRequestForm(forms.ModelForm):
    class Meta:
        model = ActivationRequest
        fields = ['restaurant_name', 'message']


@login_required
def request_activation(request):
    if request.method == 'POST':
        form = ActivationRequestForm(request.POST)
        if form.is_valid():
            activation_request = form.save(commit=False)
            activation_request.user = request.user
            activation_request.save()
            return redirect('activation_request_success')
    else:
        form = ActivationRequestForm()

    return render(request, 'user/request_activation.html', {'form': form})


@login_required
def activation_request_success(request):
    return render(request, 'user/activation_request_success.html')


@staff_member_required
def review_activation_requests(request):
    requests = ActivationRequest.objects.filter(status='pending')
    return render(request, 'user/review_activation_requests.html', {'requests': requests})


@staff_member_required
def update_activation_request(request, request_id, status):
    activation_request = get_object_or_404(ActivationRequest, id=request_id)
    activation_request.status = status
    activation_request.save()
    # Thêm logic để kích hoạt user nếu cần thiết
    if status == 'approved':
        activation_request.user.is_active = True
        activation_request.user.save()
    return redirect('review_activation_requests')



