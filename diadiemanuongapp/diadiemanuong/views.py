from django.contrib.admin import action
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views import View
from rest_framework.decorators import action
from rest_framework import viewsets, generics, status, permissions, parsers, filters, request
from rest_framework.response import Response
from rest_framework.utils import json

from . import perms
from .paginator import RestaurantPaginator, DishPaginator, UserPaginator
from .serializer import CategorySerializer, RestaurantSerializer, DishSerializer, UserSerializer, CommentSerializer, \
    DishSerializerDetail, OrderSerializer, OrderDetailSerializer, RatingSerializer
from .models import Category, Restaurant, Dish, User, Comment, Like, Order, OrderDetail, Rating
from oauth2_provider.models import AccessToken
from django.db.models import Q, Sum


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

    @action(methods=['get'], url_path='comment', detail=True)
    def get(self, request, pk):
        comments = Comment.objects.filter(dish=self.get_object())

        serializer = CommentSerializer(comments, many=True)
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

    @action(methods=['get'], url_path="current", detail=False)
    def get_queryset(self):
        username = self.request.user.username
        return Order.objects.filter(username__contains=username)

    @action(methods=['post'], url_path='order', detail=True)
    def post(self, request):
    #     serializer = OrderSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # if request.method == 'POST':
        #     order = OrderViewSet(request.POST)
        #     order_detail = [OrderDetailViewSet(request.POST, prefix=str(i)) for i in
        #                           range(request.POST.get('num_order_details', 0))]
        #
        #     if order.is_valid() and all(order_detail_form.is_valid() for order_detail_form in order_detail):
        #         order = order.save()
        #
        #         for order_detail_form in order_detail:
        #             order_detail = order_detail_form.save(commit=False)
        #             order_detail.order = order
        #             order_detail.save()
        #
        #         return redirect('order_list')
        #
        # else:
        #     order = OrderViewSet()
        #     order_detail = [OrderDetailViewSet(prefix=str(i)) for i in range(1)]  # Initial form
        #
        # context = {
        #     'order': order,
        #     'order_detail': order_detail,
        # }
        # # return render(request, 'create_order.html', context)
        #
        # return Response(OrderDetailSerializer(order_detail, context=context).data, status=status.HTTP_201_CREATED)
        if request.method == 'POST':
            data = json.loads(request.body)
            order = Order(**data)
            try:
                order.save()
                new_order_id = order.id
                order_details_to_update = OrderDetail.objects.filter(username=order.username, order_id=None)
                for order_detail in order_details_to_update:
                    order_detail.order_id = new_order_id
                    order_detail.save()
                return JsonResponse({'new_order_id': new_order_id}, status=201)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)

class OrderDetailViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['post'], url_path='orderdetail', detail=True)
    def post(self, request):
        serializer = OrderDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path="orderdetail", detail=False)
    def get_queryset(self):
        username = self.request.user.username
        return OrderDetail.objects.filter(username__contains=username)


