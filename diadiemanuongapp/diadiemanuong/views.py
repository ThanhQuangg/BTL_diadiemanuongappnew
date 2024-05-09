from django.contrib.admin import action
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.views import View
from rest_framework.decorators import action
from rest_framework import viewsets, generics, status, permissions, parsers, filters
from rest_framework.response import Response

from . import perms
from .paginator import RestaurantPaginator, DishPaginator, UserPaginator
from .serializer import CategorySerializer, RestaurantSerializer, DishSerializer, UserSerializer, CommentSerializer, \
    DishSerializerDetail, OrderSerializer
from .models import Category, Restaurant, Dish, User, Comment, Like, Order, OrderDetail
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
        comment = Comment.objects.create(user=request.user, dish=self.get_object(),  content=request.data.get('content'))
        comment.save()

        return Response(CommentSerializer(comment.data, context={
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
    # def get_queryset(self):
    #     queries = self.queryset
    #     user = self.request.query_params.get('user')
    #     if user:
    #         queries = queries.filter(id__icontains=user)
    #         return queries
    #     return Order.objects.all()

    # def get_queryset(self):
    #     queries = self.queryset
    #     x = self.request.query_params.get('x')
    #     if x:
    #         queries = queries.filter(name__icontains=q)
    #     return queries
    @action(methods=['post'], url_path='order', detail=True)
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
